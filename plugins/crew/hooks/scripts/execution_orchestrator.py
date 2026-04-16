#!/usr/bin/env python3
"""
Execution Orchestrator for Crew Plugin
=======================================
Externalizes Stage 4 (Execution) from crew:go's main agent context.
The main agent calls this script ONCE; it handles the full execution loop.

Architecture:
  crew:go ──(bash)──▶ execution_orchestrator.py
                        ├── parse task_plan.md → DAG
                        ├── for each wave:
                        │     ├── claude -p (Builder)
                        │     ├── git commit
                        │     ├── claude -p (Simplifier)
                        │     └── git commit (tidy)
                        └── stdout: JSON result (only thing crew:go sees)

Context cost for main agent: O(1) instead of O(N steps).
Adapted from Aethra's orchestrate.py with crew-specific extensions.
"""

import argparse
import asyncio
import json
import sys
import time
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from crew_orch_lib import (
    TaskPlanParser, StepNode,
    StateManager, SubAgentRunner, WaveCalculator,
)


# ── Result Types ─────────────────────────────────────────────────────

@dataclass
class StepResult:
    step_id: str
    status: str  # "complete" | "failed" | "skipped"
    duration_s: float = 0.0
    recovery_level: int = 0
    error: str | None = None
    commit_hash: str | None = None


@dataclass
class PostStepResult:
    committed: bool = False
    simplified: bool = False
    commit_hash: str | None = None
    tidy_hash: str | None = None


# ── Execution Orchestrator ───────────────────────────────────────────

class ExecutionOrchestrator:
    """Runs the Stage 4 execution loop externally."""

    def __init__(self, plan_path: str, state_path: str, cwd: str,
                 dry_run: bool = False, effort: str = "medium",
                 mcp_config: str | None = None, max_budget: float | None = None):
        self.plan_path = plan_path
        self.cwd = cwd
        self.dry_run = dry_run
        self.effort = effort
        self.max_budget = max_budget
        self.state = StateManager(state_path)
        self.runner = SubAgentRunner(cwd=cwd, mcp_config=mcp_config)
        self.artifacts_dir = Path(tempfile.mkdtemp(prefix="crew_exec_"))

        # Load builder prompt template
        self.builder_template = self._load_builder_template()

    def _load_builder_template(self) -> str:
        """Load the condensed builder prompt template."""
        template_path = (
            Path(__file__).parent.parent.parent
            / "_shared" / "templates" / "builder-prompt.md"
        )
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return "You are a Builder agent. Implement the step described below. Commit after completion."

    # ── Main Entry ───────────────────────────────────────────────────

    async def run(self) -> str:
        """Execute the full pipeline. Returns JSON to stdout."""
        t_start = time.monotonic()

        # Parse task plan
        content = Path(self.plan_path).read_text(encoding="utf-8")
        parser = TaskPlanParser(content)
        pending = parser.parse_pending()

        if not pending:
            return self._success_output([], 0.0)

        # Calculate waves
        waves = WaveCalculator.calculate(pending)
        total_steps = len(pending)

        self._log(f"Execution: {total_steps} steps, {len(waves)} waves")
        self._log(f"Artifacts: {self.artifacts_dir}")

        if self.dry_run:
            return self._dry_run_output(waves, pending)

        # Execute waves sequentially, steps within wave sequentially (Phase 1)
        results: list[StepResult] = []
        completed = 0
        commits: list[dict] = []
        all_files_created: list[str] = []
        all_files_modified: list[str] = []
        consecutive_failures = 0

        for i, wave in enumerate(waves):
            self._log(f"\n── Wave {i} ({len(wave)} steps) ──")

            for step in wave:
                self._log(f"  ▶ [{step.id}] {step.description}")
                self.state.update_step(step.id, completed, total_steps)
                self.state.increment_builder_iterations()

                result = await self._execute_with_recovery(step)
                results.append(result)

                # Save artifact
                (self.artifacts_dir / f"step_{step.id}.txt").write_text(
                    json.dumps({"status": result.status, "error": result.error},
                               indent=2),
                    encoding="utf-8",
                )

                if result.status == "complete":
                    consecutive_failures = 0
                    completed += 1

                    # Post-Step Cycle
                    post = await self._post_step_cycle(step)
                    if post.commit_hash:
                        commits.append({
                            "step": step.id,
                            "hash": post.commit_hash,
                            "message": f"[feat] Step {step.id}: {step.description}",
                        })
                    if post.tidy_hash:
                        commits.append({
                            "step": step.id,
                            "hash": post.tidy_hash,
                            "message": f"[tidy] Simplify Step {step.id}",
                        })

                    # Track files
                    new_files, mod_files = await self._get_changed_files()
                    all_files_created.extend(new_files)
                    all_files_modified.extend(mod_files)

                    self._log(f"  ✓ [{step.id}] done ({result.duration_s:.1f}s)")
                elif result.status == "skipped":
                    self._log(f"  ⏭ [{step.id}] skipped")
                else:
                    consecutive_failures += 1
                    self.state.record_error("execution", step.id, result.error or "unknown")
                    self._log(f"  ✗ [{step.id}] failed (recovery level {result.recovery_level})")

                    if consecutive_failures >= 3:
                        self._log("  ⚠ 3 consecutive failures — aborting")
                        return self._error_output(
                            results, completed, total_steps, commits,
                            f"3 consecutive failures at step {step.id}",
                        )

                self.state.update_step(
                    step.id, completed, total_steps,
                    all_files_created, all_files_modified,
                )

        total_s = time.monotonic() - t_start
        return self._success_output(
            results, total_s, completed, total_steps, commits,
            all_files_created, all_files_modified,
        )

    # ── Builder Execution ────────────────────────────────────────────

    async def _run_builder(self, step: StepNode, extra_context: str = "") -> str:
        """Run a Builder sub-agent via claude -p."""
        prompt = self._build_prompt(step, extra_context)
        return await self.runner.run_or_raise(
            prompt, effort=self.effort, max_budget=self.max_budget,
        )

    def _build_prompt(self, step: StepNode, extra_context: str = "") -> str:
        """Construct the full prompt for a Builder sub-agent."""
        parts = [self.builder_template]

        parts.append(f"\n## Your Task\n\nImplement Step {step.id}: {step.description}")

        if step.notes:
            parts.append(f"\nNotes: {step.notes}")

        if step.context_files:
            files_str = ", ".join(f"`{f}`" for f in step.context_files)
            parts.append(f"\nRelevant files: {files_str}")

        if extra_context:
            parts.append(f"\n## Additional Context\n\n{extra_context}")

        parts.append(
            "\n## Important\n"
            "- Do NOT output any SIGNAL lines\n"
            "- Commit your changes when done\n"
            "- If tests exist, run them and ensure they pass"
        )

        return "\n".join(parts)

    # ── 5-Level Error Recovery ───────────────────────────────────────

    async def _execute_with_recovery(self, step: StepNode) -> StepResult:
        """Execute a step with 5-level recovery cascade."""
        last_error = ""
        t0 = time.monotonic()

        for level in range(5):
            try:
                if level == 0:
                    await self._run_builder(step)
                elif level == 1:
                    # Retry with error context
                    await self._run_builder(
                        step,
                        extra_context=f"Previous attempt failed: {last_error}\nPlease try a different approach.",
                    )
                elif level == 2:
                    # Fixer agent
                    await self._run_fixer(step, last_error)
                elif level == 3:
                    # Skip if non-blocking
                    if self._is_non_blocking(step):
                        return StepResult(
                            step_id=step.id, status="skipped",
                            duration_s=time.monotonic() - t0,
                            recovery_level=level,
                        )
                    # Otherwise retry with simplified approach
                    await self._run_builder(
                        step,
                        extra_context=f"Multiple failures. Simplify: implement the minimum viable version.\nErrors so far: {last_error}",
                    )
                elif level == 4:
                    # Final skip for any step
                    return StepResult(
                        step_id=step.id, status="skipped",
                        duration_s=time.monotonic() - t0,
                        recovery_level=level,
                        error=f"Skipped after 5 recovery levels: {last_error}",
                    )

                return StepResult(
                    step_id=step.id, status="complete",
                    duration_s=time.monotonic() - t0,
                    recovery_level=level,
                )

            except Exception as e:
                last_error = str(e)[:300]

        # Should not reach here, but safety net
        return StepResult(
            step_id=step.id, status="failed",
            duration_s=time.monotonic() - t0,
            recovery_level=4, error=last_error,
        )

    async def _run_fixer(self, step: StepNode, error: str):
        """Run a Fixer sub-agent to patch a failure."""
        prompt = (
            f"Fix the issue from Step {step.id}: {step.description}\n\n"
            f"Error: {error}\n\n"
            "Diagnose the root cause and apply a minimal fix. Run tests to verify."
        )
        await self.runner.run_or_raise(prompt, model="haiku", effort="low")

    @staticmethod
    def _is_non_blocking(step: StepNode) -> bool:
        lower_notes = step.notes.lower()
        return "non-blocking" in lower_notes or "optional" in lower_notes

    # ── Post-Step Cycle ──────────────────────────────────────────────

    async def _post_step_cycle(self, step: StepNode) -> PostStepResult:
        """Commit → Simplify → Tidy Commit after each step."""
        result = PostStepResult()

        # Step 1: Commit changes
        status = await self._git("status", "--porcelain")
        if status.strip():
            await self._git("add", "-A")
            prefix = "[tidy]" if "tidy" in step.description.lower() else "[feat]"
            msg = f"{prefix} Step {step.id}: {step.description}"
            await self._git("commit", "-m", msg)
            result.committed = True
            result.commit_hash = (await self._git("rev-parse", "--short", "HEAD")).strip()

        # Step 2: Simplify (lightweight claude -p call)
        try:
            changed = await self._git("diff", "--name-only", "HEAD~1")
            if changed.strip():
                simplify_prompt = (
                    f"Review these recently modified files for code quality: {changed.strip()}\n"
                    "Make only clear improvements: remove dead code, fix naming, simplify logic. "
                    "Do NOT add features or change behavior."
                )
                await self.runner.run(
                    simplify_prompt, effort="low", tools="Read,Edit,Grep,Glob",
                )
                result.simplified = True
        except Exception:
            pass  # Simplification is best-effort

        # Step 3: Tidy commit
        status = await self._git("status", "--porcelain")
        if status.strip():
            await self._git("add", "-A")
            await self._git("commit", "-m", f"[tidy] Simplify Step {step.id}")
            result.tidy_hash = (await self._git("rev-parse", "--short", "HEAD")).strip()

        return result

    async def _git(self, *args: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            "git", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"git {args[0]} failed: {stderr.decode().strip()[:200]}")
        return stdout.decode()

    async def _get_changed_files(self) -> tuple[list[str], list[str]]:
        """Return (new_files, modified_files) from last commit."""
        try:
            added = await self._git("diff", "--name-only", "--diff-filter=A", "HEAD~1")
            modified = await self._git("diff", "--name-only", "--diff-filter=M", "HEAD~1")
            return (
                [f for f in added.strip().splitlines() if f],
                [f for f in modified.strip().splitlines() if f],
            )
        except Exception:
            return [], []

    # ── Output Formatters ────────────────────────────────────────────

    def _success_output(self, results: list[StepResult], total_s: float,
                        completed: int = 0, total: int = 0,
                        commits: list[dict] | None = None,
                        files_created: list[str] | None = None,
                        files_modified: list[str] | None = None) -> str:
        return json.dumps({
            "status": "success",
            "phase": "execution",
            "steps_completed": completed,
            "steps_total": total,
            "steps_failed": sum(1 for r in results if r.status == "failed"),
            "steps_skipped": sum(1 for r in results if r.status == "skipped"),
            "total_time_s": round(total_s, 1),
            "commits": commits or [],
            "step_results": {
                r.step_id: {
                    "status": r.status,
                    "duration_s": round(r.duration_s, 1),
                    "recovery_level": r.recovery_level,
                }
                for r in results
            },
            "files_created": list(set(files_created or [])),
            "files_modified": list(set(files_modified or [])),
            "errors": [
                {"step": r.step_id, "error": r.error}
                for r in results if r.error
            ],
            "artifacts_dir": str(self.artifacts_dir),
        }, ensure_ascii=False)

    def _error_output(self, results: list[StepResult], completed: int,
                      total: int, commits: list[dict], error: str) -> str:
        return json.dumps({
            "status": "error",
            "phase": "execution",
            "error": error,
            "steps_completed": completed,
            "steps_total": total,
            "commits": commits,
            "step_results": {
                r.step_id: {
                    "status": r.status,
                    "duration_s": round(r.duration_s, 1),
                    "recovery_level": r.recovery_level,
                }
                for r in results
            },
            "artifacts_dir": str(self.artifacts_dir),
        }, ensure_ascii=False)

    def _dry_run_output(self, waves: list[list[StepNode]],
                        all_steps: list[StepNode]) -> str:
        return json.dumps({
            "status": "dry_run",
            "phase": "execution",
            "steps_total": len(all_steps),
            "waves": [
                {
                    "wave": i,
                    "steps": [
                        {
                            "id": s.id,
                            "description": s.description,
                            "deps": s.deps,
                            "agent": s.agent,
                        }
                        for s in wave
                    ],
                }
                for i, wave in enumerate(waves)
            ],
        }, indent=2, ensure_ascii=False)

    @staticmethod
    def _log(msg: str):
        print(msg, file=sys.stderr, flush=True)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Crew Execution Orchestrator — externalizes Stage 4 from crew:go",
    )
    parser.add_argument("--plan", required=True, help="Path to .caw/task_plan.md")
    parser.add_argument("--state", required=True, help="Path to .caw/auto-state.json")
    parser.add_argument("--cwd", default=".", help="Project working directory")
    parser.add_argument("--dry-run", action="store_true", help="Show execution plan without running")
    parser.add_argument(
        "--effort",
        default="xhigh",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="Reasoning effort. xhigh is recommended default for Opus 4.7; max may overthink.",
    )
    parser.add_argument("--mcp-config", help="MCP server config JSON file path")
    parser.add_argument("--max-budget-usd", type=float, help="Max USD budget per Builder call")

    args = parser.parse_args()

    orchestrator = ExecutionOrchestrator(
        plan_path=args.plan,
        state_path=args.state,
        cwd=args.cwd,
        dry_run=args.dry_run,
        effort=args.effort,
        mcp_config=args.mcp_config,
        max_budget=args.max_budget_usd,
    )

    try:
        result = asyncio.run(orchestrator.run())
    except ValueError as e:
        result = json.dumps({
            "status": "error",
            "phase": "execution",
            "error": str(e),
        }, ensure_ascii=False)

    # stdout = the ONLY thing the main agent sees
    print(result)


if __name__ == "__main__":
    main()
