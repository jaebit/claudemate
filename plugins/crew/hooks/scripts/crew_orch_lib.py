"""
Crew Orchestration Library
==========================
Shared components for execution_orchestrator.py and review_orchestrator.py.
Extracted in Phase 2 to avoid code duplication across orchestrators.

Components:
  - StateManager: .caw/auto-state.json read/write
  - SubAgentRunner: claude -p subprocess wrapper
  - WaveCalculator: topological sort for step DAGs
  - TaskPlanParser re-export (from task_plan_parser.py)
"""

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path

# Re-export for convenience
from task_plan_parser import TaskPlanParser, StepNode  # noqa: F401


# ── Sub-Agent Runner ────────────────────────────────────────────────

@dataclass
class SubAgentResult:
    stdout: str
    stderr: str
    returncode: int
    duration_s: float


class SubAgentRunner:
    """Run claude -p sub-agents with configurable model/effort/tools."""

    def __init__(self, cwd: str, mcp_config: str | None = None):
        self.cwd = cwd
        self.mcp_config = mcp_config

    async def run(
        self,
        prompt: str,
        *,
        model: str | None = None,
        effort: str = "medium",
        tools: str = "Read,Write,Edit,Bash,Grep,Glob",
        max_budget: float | None = None,
        output_format: str = "text",
    ) -> SubAgentResult:
        """Execute a claude -p sub-agent and return the result."""
        t0 = time.monotonic()

        cmd = [
            "claude", "-p", prompt,
            "--output-format", output_format,
            "--allowedTools", tools,
            "--permission-mode", "auto",
            "--effort", effort,
        ]
        if model:
            cmd += ["--model", model]
        if self.mcp_config:
            cmd += ["--mcp-config", self.mcp_config]
        if max_budget:
            cmd += ["--max-budget-usd", str(max_budget)]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd,
        )
        stdout, stderr = await proc.communicate()
        duration = time.monotonic() - t0

        return SubAgentResult(
            stdout=stdout.decode().strip(),
            stderr=stderr.decode().strip(),
            returncode=proc.returncode,
            duration_s=round(duration, 1),
        )

    async def run_or_raise(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """Run a sub-agent; raise RuntimeError on non-zero exit."""
        result = await self.run(prompt, **kwargs)
        if result.returncode != 0:
            raise RuntimeError(result.stderr[:500] or "Sub-agent exited with non-zero")
        return result.stdout


# ── State Manager ───────────────────────────────────────────────────

class StateManager:
    """Read/write .caw/auto-state.json with phase-specific helpers."""

    def __init__(self, state_path: str):
        self._path = Path(state_path)
        self._state: dict = {}
        if self._path.exists():
            self._state = json.loads(self._path.read_text(encoding="utf-8"))

    @property
    def state(self) -> dict:
        return self._state

    @property
    def config(self) -> dict:
        return self._state.get("config", {})

    # ── Execution Phase Helpers ──────────────────────────────────────

    def update_step(self, step_id: str, tasks_completed: int, tasks_total: int,
                    files_created: list[str] | None = None,
                    files_modified: list[str] | None = None):
        execution = self._state.setdefault("execution", {})
        execution["current_step"] = step_id
        execution["tasks_completed"] = tasks_completed
        execution["tasks_total"] = tasks_total
        if files_created is not None:
            existing = execution.get("files_created", [])
            execution["files_created"] = list(set(existing + files_created))
        if files_modified is not None:
            existing = execution.get("files_modified", [])
            execution["files_modified"] = list(set(existing + files_modified))
        self._save()

    def increment_builder_iterations(self):
        execution = self._state.setdefault("execution", {})
        execution["builder_iterations"] = execution.get("builder_iterations", 0) + 1
        self._save()

    # ── Review Phase Helpers ─────────────────────────────────────────

    def update_review(self, verdicts: list[dict], round_num: int, all_approved: bool):
        review = self._state.setdefault("review", {})
        pv = review.setdefault("parallel_validation", {})
        pv["enabled"] = True
        pv["architects_spawned"] = 3
        pv["verdicts"] = verdicts
        pv["all_approved"] = all_approved
        pv["validation_rounds"] = round_num
        review["reviewer_iterations"] = review.get("reviewer_iterations", 0) + 1
        self._save()

    def update_fix(self, fixes_applied: int):
        fix = self._state.setdefault("fix", {})
        fix["fixer_iterations"] = fix.get("fixer_iterations", 0) + 1
        fix["fixes_applied"] = fix.get("fixes_applied", 0) + fixes_applied
        self._save()

    def record_advisor_call(self, findings: list[dict]):
        advisor = self._state.setdefault("advisor", {})
        advisor["calls_made"] = advisor.get("calls_made", 0) + 1
        decisions = advisor.setdefault("decisions", [])
        decisions.append({
            "trigger": "contested_review",
            "findings": findings,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        self._save()

    def can_call_advisor(self) -> bool:
        advisor = self._state.get("advisor", {})
        config = self._state.get("config", {})
        if not config.get("advisor_enabled", True):
            return False
        return advisor.get("calls_made", 0) < advisor.get("max_calls", 3)

    def set_review_orchestrator_artifacts(self, path: str):
        review = self._state.setdefault("review", {})
        review["orchestrator_artifacts"] = path
        self._save()

    # ── Generic Helpers ──────────────────────────────────────────────

    def record_error(self, phase: str, step: str, message: str):
        self._state["last_error"] = {
            "phase": phase,
            "step": step,
            "message": message[:500],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._save()

    def set_phase(self, phase: str):
        self._state["phase"] = phase
        self._save()

    def record_signal(self, signal: str):
        signals = self._state.setdefault("signals", {})
        detected = signals.setdefault("detected_signals", [])
        detected.append({
            "signal": signal,
            "detected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        signals["last_checked"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._save()

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


# ── Wave Calculator ─────────────────────────────────────────────────

class WaveCalculator:
    """Group steps into execution waves via topological sort."""

    @staticmethod
    def calculate(steps: list[StepNode]) -> list[list[StepNode]]:
        step_map = {s.id: s for s in steps}
        all_ids = {s.id for s in steps}

        in_degree = {}
        for s in steps:
            relevant_deps = [d for d in s.deps if d in all_ids]
            in_degree[s.id] = len(relevant_deps)

        remaining = set(all_ids)
        waves: list[list[StepNode]] = []

        while remaining:
            wave_ids = sorted(sid for sid in remaining if in_degree[sid] == 0)
            if not wave_ids:
                raise ValueError(f"Circular dependency among: {remaining}")
            waves.append([step_map[sid] for sid in wave_ids])
            for sid in wave_ids:
                remaining.discard(sid)
                for other in steps:
                    if sid in other.deps and other.id in remaining:
                        in_degree[other.id] -= 1

        return waves
