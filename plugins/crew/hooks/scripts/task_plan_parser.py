"""
Task Plan Parser
================
Parses .caw/task_plan.md markdown into structured StepNode data.
Used by the execution orchestrator to build a DAG of steps.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class StepNode:
    id: str
    phase: int
    description: str
    status: str  # "pending" | "complete" | "in_progress" | "skipped"
    agent: str
    deps: list[str] = field(default_factory=list)
    notes: str = ""
    context_files: list[str] = field(default_factory=list)


# ── Status Mapping ───────────────────────────────────────────────────

STATUS_MAP = {
    "✅": "complete",
    "Complete": "complete",
    "🔄": "in_progress",
    "In Progress": "in_progress",
    "⏳": "pending",
    "Pending": "pending",
    "⏭️": "skipped",
    "Skipped": "skipped",
    "🚫": "skipped",
    "Blocked": "blocked",
}


# ── Parser ───────────────────────────────────────────────────────────

class TaskPlanParser:
    """Parse .caw/task_plan.md into a list of StepNode objects."""

    # Matches markdown table rows: | 2.1 | description | status | agent | deps | notes |
    ROW_RE = re.compile(
        r"^\|\s*"
        r"(?P<id>\d+\.\d+)\s*\|\s*"
        r"(?P<desc>[^|]+?)\s*\|\s*"
        r"(?P<status>[^|]+?)\s*\|\s*"
        r"(?P<agent>[^|]+?)\s*\|\s*"
        r"(?P<deps>[^|]*?)\s*\|\s*"
        r"(?P<notes>[^|]*?)\s*\|"
    )

    # Matches phase headers: ### Phase 2: Core Implementation
    PHASE_RE = re.compile(r"^###\s+Phase\s+(\d+):\s*(.*)")

    # Matches context file entries: - `src/auth/jwt.ts` - description
    CONTEXT_FILE_RE = re.compile(r"^-\s+`([^`]+)`")

    def __init__(self, content: str):
        self._content = content
        self._all_steps: list[StepNode] = []
        self._phase_steps: dict[int, list[str]] = {}  # phase -> [step_ids]
        self._phase_context: dict[int, list[str]] = {}  # phase -> [file_paths]

    def parse(self) -> list[StepNode]:
        """Parse markdown content and return all steps."""
        self._extract_context_files()
        self._extract_steps()
        self._resolve_wildcard_deps()
        return self._all_steps

    def parse_pending(self) -> list[StepNode]:
        """Parse and return only pending/in_progress steps."""
        all_steps = self.parse()
        return [s for s in all_steps if s.status in ("pending", "in_progress")]

    # ── Internal ─────────────────────────────────────────────────────

    def _extract_context_files(self):
        """Extract per-phase context files from Active Context sections."""
        current_phase = 0
        in_active_context = False

        for line in self._content.splitlines():
            phase_match = self.PHASE_RE.match(line)
            if phase_match:
                current_phase = int(phase_match.group(1))
                in_active_context = False
                continue

            if "Active Context" in line or "will be modified" in line:
                in_active_context = True
                continue

            if in_active_context:
                if line.startswith("###") or line.startswith("## ") or "Context" in line:
                    in_active_context = False
                    continue
                ctx_match = self.CONTEXT_FILE_RE.match(line.strip())
                if ctx_match:
                    self._phase_context.setdefault(current_phase, []).append(
                        ctx_match.group(1)
                    )

        # Global context (phase 0) applies to all phases
        if 0 in self._phase_context:
            global_ctx = self._phase_context[0]
            for phase in self._phase_context:
                if phase != 0:
                    self._phase_context[phase] = global_ctx + self._phase_context[phase]

    def _extract_steps(self):
        """Extract steps from markdown table rows."""
        current_phase = 0

        for line in self._content.splitlines():
            phase_match = self.PHASE_RE.match(line)
            if phase_match:
                current_phase = int(phase_match.group(1))
                continue

            row_match = self.ROW_RE.match(line)
            if not row_match:
                continue

            step_id = row_match.group("id").strip()
            raw_status = row_match.group("status").strip()
            raw_deps = row_match.group("deps").strip()

            status = self._parse_status(raw_status)
            deps = self._parse_deps(raw_deps)
            phase = int(step_id.split(".")[0]) if "." in step_id else current_phase

            step = StepNode(
                id=step_id,
                phase=phase,
                description=row_match.group("desc").strip(),
                status=status,
                agent=row_match.group("agent").strip(),
                deps=deps,
                notes=row_match.group("notes").strip(),
                context_files=list(self._phase_context.get(phase, [])),
            )

            self._all_steps.append(step)
            self._phase_steps.setdefault(phase, []).append(step_id)

    def _parse_status(self, raw: str) -> str:
        """Map emoji/text status to normalized status string."""
        for marker, status in STATUS_MAP.items():
            if marker in raw:
                return status
        return "pending"

    def _parse_deps(self, raw: str) -> list[str]:
        """Parse dependency string: '1.1, 1.2' or '1.*' or '-'."""
        if not raw or raw.strip() == "-" or raw.strip() == "":
            return []
        parts = [d.strip() for d in raw.split(",")]
        return [p for p in parts if p]

    def _resolve_wildcard_deps(self):
        """Expand wildcard deps like '1.*' to actual step IDs."""
        for step in self._all_steps:
            resolved: list[str] = []
            for dep in step.deps:
                if dep.endswith(".*"):
                    phase_num = int(dep.split(".")[0])
                    phase_ids = self._phase_steps.get(phase_num, [])
                    resolved.extend(phase_ids)
                else:
                    resolved.append(dep)
            step.deps = resolved


# ── Convenience Function ─────────────────────────────────────────────

def parse_task_plan(path: str | Path) -> list[StepNode]:
    """Parse a task plan file and return all steps."""
    content = Path(path).read_text(encoding="utf-8")
    return TaskPlanParser(content).parse()


def parse_pending_steps(path: str | Path) -> list[StepNode]:
    """Parse a task plan file and return only pending/in_progress steps."""
    content = Path(path).read_text(encoding="utf-8")
    return TaskPlanParser(content).parse_pending()
