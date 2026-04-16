#!/usr/bin/env python3
"""
Review Orchestrator for Crew Plugin
====================================
Externalizes Stage 6-7 (Review + Fix) from crew:go's main agent context.
Runs a Diamond DAG: 3 parallel Reviewers → aggregate → advisor triage → fixer.

Architecture (Diamond DAG):
  review-functional ──┐
  review-security  ──┼──▶ aggregate ──▶ [contested?] ──▶ advisor-triage ──▶ fixer
  review-quality   ──┘                   [unanimous?] ──▶ done

Model routing:
  - Reviewers:    sonnet (default)
  - Advisor:      opus  (contested triage only)
  - Fixer:        haiku (cheap, targeted fixes)

Max 3 review-fix rounds. JSON output to stdout.
"""

import argparse
import asyncio
import json
import re
import sys
import time
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from crew_orch_lib import StateManager, SubAgentRunner


# ── Constants ───────────────────────────────────────────────────────

REVIEWER_TYPES = ("functional", "security", "quality")
MAX_ROUNDS = 3


# ── Data Types ──────────────────────────────────────────────────────

@dataclass
class ReviewIssue:
    severity: str   # "critical" | "major" | "minor"
    file: str
    line: int
    description: str
    suggestion: str
    reviewer_type: str = ""
    owasp: str = ""

    def to_dict(self) -> dict:
        d = {
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "suggestion": self.suggestion,
        }
        if self.reviewer_type:
            d["reviewer_type"] = self.reviewer_type
        if self.owasp:
            d["owasp"] = self.owasp
        return d


@dataclass
class ReviewVerdict:
    reviewer_type: str   # "functional" | "security" | "quality"
    verdict: str         # "APPROVED" | "REJECTED" | "NEEDS_FIX"
    issues: list[ReviewIssue] = field(default_factory=list)
    summary: str = ""
    duration_s: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "type": self.reviewer_type,
            "verdict": self.verdict,
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


@dataclass
class RoundResult:
    round_num: int
    verdicts: list[ReviewVerdict]
    final_verdict: str  # "APPROVED" | "REJECTED" | "NEEDS_FIX"
    issues_count: int
    advisor_used: bool = False
    fixes_applied: int = 0


# ── Review Orchestrator ─────────────────────────────────────────────

class ReviewOrchestrator:
    """Runs the Stage 6-7 review/fix loop externally."""

    def __init__(
        self,
        state_path: str,
        cwd: str,
        max_rounds: int = MAX_ROUNDS,
        dry_run: bool = False,
        mcp_config: str | None = None,
        spec_path: str | None = None,
    ):
        self.cwd = cwd
        self.max_rounds = max_rounds
        self.dry_run = dry_run
        self.spec_path = spec_path or ".caw/spec.md"
        self.state = StateManager(state_path)
        self.runner = SubAgentRunner(cwd=cwd, mcp_config=mcp_config)
        self.artifacts_dir = Path(tempfile.mkdtemp(prefix="crew_review_"))

        # Load reviewer prompt templates
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[str, str]:
        """Load the 3 reviewer prompt templates."""
        templates_dir = (
            Path(__file__).parent.parent.parent
            / "_shared" / "templates"
        )
        templates = {}
        for rtype in REVIEWER_TYPES:
            path = templates_dir / f"reviewer-{rtype}.md"
            if path.exists():
                templates[rtype] = path.read_text(encoding="utf-8")
            else:
                templates[rtype] = f"Review code for {rtype} issues. Output JSON with verdict and issues."
        return templates

    # ── Main Entry ───────────────────────────────────────────────────

    async def run(self) -> str:
        """Execute the full review/fix Diamond DAG. Returns JSON to stdout."""
        t_start = time.monotonic()

        # Discover files to review from execution state or git
        files = await self._discover_review_files()
        if not files:
            return self._output("success", rounds=[], total_s=0.0,
                                message="No files to review")

        self._log(f"Review: {len(files)} files, max {self.max_rounds} rounds")
        self._log(f"Artifacts: {self.artifacts_dir}")

        if self.dry_run:
            return self._dry_run_output(files)

        self.state.set_review_orchestrator_artifacts(str(self.artifacts_dir))

        rounds: list[RoundResult] = []

        for round_num in range(1, self.max_rounds + 1):
            self._log(f"\n── Round {round_num}/{self.max_rounds} ──")

            # Step 1: Fan-out — 3 parallel reviewers
            verdicts = await self._run_parallel_reviews(files, round_num)

            # Step 2: Aggregate verdicts
            final_verdict, all_issues = self._aggregate_verdicts(verdicts)
            self._log(f"  Aggregate: {final_verdict} ({len(all_issues)} issues)")

            # Step 3: Contested? → Advisor triage
            advisor_used = False
            if self._is_contested(verdicts) and self.state.can_call_advisor():
                self._log("  Verdicts contested → advisor triage")
                genuine, false_positives = await self._advisor_triage(verdicts, files)
                advisor_used = True

                # Filter: only genuine issues go to fixer
                all_issues = genuine
                if not all_issues:
                    final_verdict = "APPROVED"
                    self._log(f"  Advisor: all issues false-positive → APPROVED")

            # Update state
            verdict_dicts = [v.to_dict() for v in verdicts]
            all_approved = final_verdict == "APPROVED"
            self.state.update_review(verdict_dicts, round_num, all_approved)

            # Save round artifact
            round_result = RoundResult(
                round_num=round_num,
                verdicts=verdicts,
                final_verdict=final_verdict,
                issues_count=len(all_issues),
                advisor_used=advisor_used,
            )

            # Step 4: If approved, done
            if final_verdict == "APPROVED":
                self._log(f"  ✓ All approved in round {round_num}")
                rounds.append(round_result)
                break

            # Step 5: Fix issues
            fixes_applied = await self._run_fixer(all_issues)
            round_result.fixes_applied = fixes_applied
            self.state.update_fix(fixes_applied)
            self._log(f"  Fixed {fixes_applied}/{len(all_issues)} issues")

            rounds.append(round_result)

            # Commit fixes
            await self._commit_fixes(round_num)

        total_s = time.monotonic() - t_start
        final = rounds[-1].final_verdict if rounds else "APPROVED"

        status = "success" if final == "APPROVED" else "needs_intervention"
        return self._output(status, rounds=rounds, total_s=total_s)

    # ── Parallel Reviews (Fan-Out) ──────────────────────────────────

    async def _run_parallel_reviews(
        self, files: list[str], round_num: int,
    ) -> list[ReviewVerdict]:
        """Run 3 reviewer sub-agents in parallel."""
        files_str = "\n".join(f"- `{f}`" for f in files)

        tasks = []
        for rtype in REVIEWER_TYPES:
            prompt = self._build_reviewer_prompt(rtype, files_str)
            tasks.append(self._run_single_reviewer(rtype, prompt))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        verdicts = []
        for rtype, result in zip(REVIEWER_TYPES, results):
            if isinstance(result, Exception):
                self._log(f"  ✗ {rtype} reviewer failed: {result}")
                verdicts.append(ReviewVerdict(
                    reviewer_type=rtype, verdict="NEEDS_FIX",
                    summary=f"Reviewer error: {str(result)[:200]}",
                    error=str(result)[:200],
                ))
            else:
                verdicts.append(result)
            self._log(f"  {rtype}: {verdicts[-1].verdict}")

        return verdicts

    async def _run_single_reviewer(
        self, rtype: str, prompt: str,
    ) -> ReviewVerdict:
        """Run one reviewer and parse its JSON output."""
        t0 = time.monotonic()
        result = await self.runner.run(
            prompt,
            model="sonnet",
            effort="medium",
            tools="Read,Grep,Glob,Bash",
        )
        duration = time.monotonic() - t0

        if result.returncode != 0:
            raise RuntimeError(result.stderr[:300] or f"{rtype} reviewer exited non-zero")

        # Parse JSON from output
        parsed = self._parse_reviewer_json(result.stdout, rtype)
        parsed.duration_s = round(duration, 1)
        return parsed

    def _build_reviewer_prompt(self, rtype: str, files_str: str) -> str:
        """Construct the full prompt for a reviewer sub-agent."""
        template = self.templates[rtype]

        # Substitute template variables
        prompt = template.replace("{files}", files_str)
        prompt = prompt.replace("{spec_path}", self.spec_path)

        return prompt

    def _parse_reviewer_json(self, output: str, rtype: str) -> ReviewVerdict:
        """Parse reviewer output into ReviewVerdict. Tolerant of non-JSON wrapping."""
        # Try to extract JSON from output (may be wrapped in markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', output)
        if not json_match:
            return ReviewVerdict(
                reviewer_type=rtype, verdict="NEEDS_FIX",
                summary="Could not parse reviewer output as JSON",
                error="No JSON found in output",
            )

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            return ReviewVerdict(
                reviewer_type=rtype, verdict="NEEDS_FIX",
                summary=f"Invalid JSON from reviewer: {e}",
                error=str(e),
            )

        verdict = data.get("verdict", "NEEDS_FIX")
        if verdict not in ("APPROVED", "REJECTED", "NEEDS_FIX"):
            verdict = "NEEDS_FIX"

        issues = []
        for raw in data.get("issues", []):
            issues.append(ReviewIssue(
                severity=raw.get("severity", "minor"),
                file=raw.get("file", ""),
                line=raw.get("line", 0),
                description=raw.get("description", ""),
                suggestion=raw.get("suggestion", ""),
                reviewer_type=rtype,
                owasp=raw.get("owasp", ""),
            ))

        return ReviewVerdict(
            reviewer_type=rtype,
            verdict=verdict,
            issues=issues,
            summary=data.get("summary", ""),
        )

    # ── Verdict Aggregation ─────────────────────────────────────────

    @staticmethod
    def _aggregate_verdicts(
        verdicts: list[ReviewVerdict],
    ) -> tuple[str, list[ReviewIssue]]:
        """Aggregate 3 reviewer verdicts. Any REJECTED → REJECTED."""
        all_issues: list[ReviewIssue] = []
        for v in verdicts:
            all_issues.extend(v.issues)

        if any(v.verdict == "REJECTED" for v in verdicts):
            return "REJECTED", all_issues

        if any(v.verdict == "NEEDS_FIX" for v in verdicts):
            return "NEEDS_FIX", all_issues

        return "APPROVED", all_issues

    @staticmethod
    def _is_contested(verdicts: list[ReviewVerdict]) -> bool:
        """Check if verdicts are split (not unanimous)."""
        non_error = [v for v in verdicts if v.error is None]
        if len(non_error) < 2:
            return False
        verdict_set = {v.verdict for v in non_error}
        return len(verdict_set) > 1

    # ── Advisor Triage ──────────────────────────────────────────────

    async def _advisor_triage(
        self,
        verdicts: list[ReviewVerdict],
        files: list[str],
    ) -> tuple[list[ReviewIssue], list[ReviewIssue]]:
        """
        Consult Opus advisor to triage contested findings.
        Returns (genuine_issues, false_positives).
        """
        # Build conflict summary
        verdict_details = "\n".join(
            f"- {v.reviewer_type}: {v.verdict} — {v.summary}"
            for v in verdicts
        )
        all_issues = []
        for v in verdicts:
            all_issues.extend(v.issues)

        issues_detail = "\n".join(
            f"- [{i.reviewer_type}] {i.severity}: {i.file}:{i.line} — {i.description}"
            for i in all_issues
        )

        prompt = (
            "You are an Advisor providing diagnostic judgment. You have NO tools.\n"
            "Respond in under 500 tokens with a structured decision.\n\n"
            "## Situation\n"
            "contested_review: Reviewer verdicts are split on code quality.\n\n"
            "## Context\n"
            f"- Reviewer verdicts:\n{verdict_details}\n"
            f"- Files involved: {', '.join(files[:10])}\n\n"
            "## Issues to Triage\n"
            f"{issues_detail}\n\n"
            "## Your Task\n"
            "For each issue, classify as:\n"
            "- GENUINE: Real issue that needs fixing. Reason: ...\n"
            "- FALSE_POSITIVE: Not a real issue. Reason: ...\n\n"
            "Output ONLY a JSON array:\n"
            '```json\n[{"issue_index": 0, "classification": "GENUINE|FALSE_POSITIVE", '
            '"reasoning": "..."}]\n```'
        )

        result = await self.runner.run(
            prompt, model="opus", effort="low", tools="",
        )

        # Parse advisor response
        genuine: list[ReviewIssue] = []
        false_positives: list[ReviewIssue] = []
        findings_for_state: list[dict] = []

        if result.returncode == 0:
            classifications = self._parse_advisor_json(result.stdout, len(all_issues))
            for idx, issue in enumerate(all_issues):
                cls = classifications.get(idx, "GENUINE")  # default to genuine if unparsed
                findings_for_state.append({
                    "classification": cls,
                    "issue": issue.description[:100],
                    "reasoning": classifications.get(f"{idx}_reason", ""),
                })
                if cls == "GENUINE":
                    genuine.append(issue)
                else:
                    false_positives.append(issue)
        else:
            # Advisor failed — treat all as genuine (conservative)
            self._log(f"  ⚠ Advisor failed, treating all issues as genuine")
            genuine = all_issues

        self.state.record_advisor_call(findings_for_state)
        self._log(f"  Advisor: {len(genuine)} genuine, {len(false_positives)} false-positive")
        return genuine, false_positives

    def _parse_advisor_json(
        self, output: str, issue_count: int,
    ) -> dict[int | str, str]:
        """Parse advisor classification array. Returns {index: classification, index_reason: reasoning}."""
        result: dict[int | str, str] = {}
        json_match = re.search(r'\[[\s\S]*\]', output)
        if not json_match:
            return result
        try:
            items = json.loads(json_match.group())
            for item in items:
                idx = item.get("issue_index", -1)
                if 0 <= idx < issue_count:
                    cls = item.get("classification", "GENUINE")
                    result[idx] = cls if cls in ("GENUINE", "FALSE_POSITIVE") else "GENUINE"
                    result[f"{idx}_reason"] = item.get("reasoning", "")
        except (json.JSONDecodeError, TypeError):
            pass
        return result

    # ── Fixer ───────────────────────────────────────────────────────

    async def _run_fixer(self, issues: list[ReviewIssue]) -> int:
        """Run Fixer sub-agent to address review issues. Returns count of fixes applied."""
        if not issues:
            return 0

        issues_text = "\n".join(
            f"- [{i.severity}] {i.file}:{i.line} — {i.description}\n"
            f"  Suggestion: {i.suggestion}"
            for i in issues
        )

        prompt = (
            "You are a Fixer agent. Apply minimal, targeted fixes for the issues below.\n\n"
            "## Issues\n"
            f"{issues_text}\n\n"
            "## Rules\n"
            "- Fix each issue with the minimum change needed\n"
            "- Do NOT refactor surrounding code\n"
            "- Do NOT add features\n"
            "- Run tests after fixing to ensure no regressions\n"
            "- Report how many issues you fixed\n\n"
            "Output the count of fixed issues as the last line: FIXED: N"
        )

        result = await self.runner.run(
            prompt, model="haiku", effort="low",
        )

        if result.returncode != 0:
            self._log(f"  ⚠ Fixer failed: {result.stderr[:200]}")
            return 0

        # Parse fix count from output
        match = re.search(r'FIXED:\s*(\d+)', result.stdout)
        return int(match.group(1)) if match else len(issues)

    # ── Git Helpers ─────────────────────────────────────────────────

    async def _commit_fixes(self, round_num: int):
        """Commit any outstanding changes from the fixer."""
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--porcelain",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )
        stdout, _ = await proc.communicate()
        if not stdout.decode().strip():
            return

        await asyncio.create_subprocess_exec(
            "git", "add", "-A",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )
        await asyncio.create_subprocess_exec(
            "git", "commit", "-m", f"[fix] Review round {round_num} fixes",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )

    async def _discover_review_files(self) -> list[str]:
        """Discover files to review from execution state or recent git changes."""
        # Try execution state first
        execution = self.state.state.get("execution", {})
        files_created = execution.get("files_created", [])
        files_modified = execution.get("files_modified", [])
        files = list(set(files_created + files_modified))

        if files:
            return files

        # Fallback: get files changed since the branch diverged
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "diff", "--name-only", "HEAD~5",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode == 0:
                return [f for f in stdout.decode().strip().splitlines() if f]
        except Exception:
            pass

        return []

    # ── Output Formatters ───────────────────────────────────────────

    def _output(
        self,
        status: str,
        rounds: list[RoundResult],
        total_s: float,
        message: str = "",
    ) -> str:
        total_issues = sum(r.issues_count for r in rounds)
        total_fixes = sum(r.fixes_applied for r in rounds)
        final_verdict = rounds[-1].final_verdict if rounds else "APPROVED"

        return json.dumps({
            "status": status,
            "phase": "review",
            "final_verdict": final_verdict,
            "rounds_used": len(rounds),
            "max_rounds": self.max_rounds,
            "total_issues_found": total_issues,
            "total_fixes_applied": total_fixes,
            "total_time_s": round(total_s, 1),
            "advisor_used": any(r.advisor_used for r in rounds),
            "rounds": [
                {
                    "round": r.round_num,
                    "verdicts": [v.to_dict() for v in r.verdicts],
                    "final_verdict": r.final_verdict,
                    "issues_count": r.issues_count,
                    "advisor_used": r.advisor_used,
                    "fixes_applied": r.fixes_applied,
                }
                for r in rounds
            ],
            "message": message,
            "artifacts_dir": str(self.artifacts_dir),
        }, ensure_ascii=False)

    def _dry_run_output(self, files: list[str]) -> str:
        return json.dumps({
            "status": "dry_run",
            "phase": "review",
            "files_to_review": files,
            "reviewer_types": list(REVIEWER_TYPES),
            "max_rounds": self.max_rounds,
            "advisor_available": self.state.can_call_advisor(),
        }, indent=2, ensure_ascii=False)

    @staticmethod
    def _log(msg: str):
        print(msg, file=sys.stderr, flush=True)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Crew Review Orchestrator — externalizes Stage 6-7 from crew:go",
    )
    parser.add_argument("--state", required=True, help="Path to .caw/auto-state.json")
    parser.add_argument("--cwd", default=".", help="Project working directory")
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS, help="Max review-fix rounds")
    parser.add_argument("--dry-run", action="store_true", help="Show review plan without running")
    parser.add_argument("--mcp-config", help="MCP server config JSON file path")
    parser.add_argument("--spec", help="Path to spec.md for functional review")

    args = parser.parse_args()

    orchestrator = ReviewOrchestrator(
        state_path=args.state,
        cwd=args.cwd,
        max_rounds=args.max_rounds,
        dry_run=args.dry_run,
        mcp_config=args.mcp_config,
        spec_path=args.spec,
    )

    try:
        result = asyncio.run(orchestrator.run())
    except Exception as e:
        result = json.dumps({
            "status": "error",
            "phase": "review",
            "error": str(e),
        }, ensure_ascii=False)

    print(result)


if __name__ == "__main__":
    main()
