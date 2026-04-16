"""Tests for review_orchestrator.py and crew_orch_lib.py"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

# Add hooks/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "scripts"))

from crew_orch_lib import StateManager, SubAgentRunner, SubAgentResult, WaveCalculator
from task_plan_parser import StepNode
from review_orchestrator import (
    ReviewOrchestrator, ReviewVerdict, ReviewIssue, REVIEWER_TYPES,
)


# ── crew_orch_lib Tests ─────────────────────────────────────────────


class TestStateManagerReview:
    """Test StateManager review/fix/advisor helpers."""

    def test_update_review(self, tmp_path):
        state_file = tmp_path / ".caw" / "auto-state.json"
        state_file.parent.mkdir(parents=True)
        state_file.write_text('{"config": {"advisor_enabled": true}}')

        mgr = StateManager(str(state_file))
        verdicts = [
            {"type": "functional", "verdict": "APPROVED", "issues": []},
            {"type": "security", "verdict": "NEEDS_FIX", "issues": [{"severity": "major"}]},
            {"type": "quality", "verdict": "APPROVED", "issues": []},
        ]
        mgr.update_review(verdicts, round_num=1, all_approved=False)

        saved = json.loads(state_file.read_text())
        pv = saved["review"]["parallel_validation"]
        assert pv["enabled"] is True
        assert pv["architects_spawned"] == 3
        assert pv["validation_rounds"] == 1
        assert pv["all_approved"] is False
        assert len(pv["verdicts"]) == 3

    def test_update_fix(self, tmp_path):
        state_file = tmp_path / ".caw" / "auto-state.json"
        state_file.parent.mkdir(parents=True)
        state_file.write_text("{}")

        mgr = StateManager(str(state_file))
        mgr.update_fix(3)
        mgr.update_fix(2)

        saved = json.loads(state_file.read_text())
        assert saved["fix"]["fixer_iterations"] == 2
        assert saved["fix"]["fixes_applied"] == 5

    def test_can_call_advisor_enabled(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "config": {"advisor_enabled": True},
            "advisor": {"calls_made": 1, "max_calls": 3},
        }))

        mgr = StateManager(str(state_file))
        assert mgr.can_call_advisor() is True

    def test_can_call_advisor_exhausted(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "config": {"advisor_enabled": True},
            "advisor": {"calls_made": 3, "max_calls": 3},
        }))

        mgr = StateManager(str(state_file))
        assert mgr.can_call_advisor() is False

    def test_can_call_advisor_disabled(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "config": {"advisor_enabled": False},
            "advisor": {"calls_made": 0, "max_calls": 3},
        }))

        mgr = StateManager(str(state_file))
        assert mgr.can_call_advisor() is False

    def test_record_advisor_call(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "config": {"advisor_enabled": True},
            "advisor": {"calls_made": 0, "max_calls": 3, "decisions": []},
        }))

        mgr = StateManager(str(state_file))
        mgr.record_advisor_call([
            {"classification": "GENUINE", "issue": "SQL injection", "reasoning": "user input unsanitized"},
            {"classification": "FALSE_POSITIVE", "issue": "naming", "reasoning": "project convention"},
        ])

        saved = json.loads(state_file.read_text())
        assert saved["advisor"]["calls_made"] == 1
        assert len(saved["advisor"]["decisions"]) == 1
        assert saved["advisor"]["decisions"][0]["trigger"] == "contested_review"
        assert len(saved["advisor"]["decisions"][0]["findings"]) == 2

    def test_record_error(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text("{}")

        mgr = StateManager(str(state_file))
        mgr.record_error("review", "round_1", "timeout after 60s")

        saved = json.loads(state_file.read_text())
        assert saved["last_error"]["phase"] == "review"
        assert saved["last_error"]["step"] == "round_1"
        assert "timeout" in saved["last_error"]["message"]


class TestWaveCalculator:
    """Test WaveCalculator topological sort."""

    def test_simple_chain(self):
        steps = [
            StepNode(id="1.1", phase=1, description="A", status="pending", agent="Builder"),
            StepNode(id="1.2", phase=1, description="B", status="pending", agent="Builder", deps=["1.1"]),
            StepNode(id="1.3", phase=1, description="C", status="pending", agent="Builder", deps=["1.2"]),
        ]
        waves = WaveCalculator.calculate(steps)
        assert len(waves) == 3
        assert [s.id for s in waves[0]] == ["1.1"]
        assert [s.id for s in waves[1]] == ["1.2"]
        assert [s.id for s in waves[2]] == ["1.3"]

    def test_parallel_wave(self):
        steps = [
            StepNode(id="1.1", phase=1, description="A", status="pending", agent="Builder"),
            StepNode(id="2.1", phase=2, description="B", status="pending", agent="Builder", deps=["1.1"]),
            StepNode(id="2.2", phase=2, description="C", status="pending", agent="Builder", deps=["1.1"]),
        ]
        waves = WaveCalculator.calculate(steps)
        assert len(waves) == 2
        wave_ids = [s.id for s in waves[1]]
        assert set(wave_ids) == {"2.1", "2.2"}

    def test_circular_dependency_raises(self):
        steps = [
            StepNode(id="1.1", phase=1, description="A", status="pending", agent="Builder", deps=["1.2"]),
            StepNode(id="1.2", phase=1, description="B", status="pending", agent="Builder", deps=["1.1"]),
        ]
        with pytest.raises(ValueError, match="Circular dependency"):
            WaveCalculator.calculate(steps)

    def test_empty_steps(self):
        waves = WaveCalculator.calculate([])
        assert waves == []


# ── Review Orchestrator Tests ───────────────────────────────────────


class TestVerdictAggregation:
    """Test ReviewOrchestrator._aggregate_verdicts."""

    def test_all_approved(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "APPROVED"),
            ReviewVerdict("quality", "APPROVED"),
        ]
        final, issues = ReviewOrchestrator._aggregate_verdicts(verdicts)
        assert final == "APPROVED"
        assert issues == []

    def test_any_rejected(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "REJECTED", issues=[
                ReviewIssue("critical", "auth.ts", 42, "SQL injection", "Use parameterized queries"),
            ]),
            ReviewVerdict("quality", "APPROVED"),
        ]
        final, issues = ReviewOrchestrator._aggregate_verdicts(verdicts)
        assert final == "REJECTED"
        assert len(issues) == 1

    def test_needs_fix_overrides_approved(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "APPROVED"),
            ReviewVerdict("quality", "NEEDS_FIX", issues=[
                ReviewIssue("minor", "utils.ts", 10, "Dead code", "Remove unused function"),
            ]),
        ]
        final, issues = ReviewOrchestrator._aggregate_verdicts(verdicts)
        assert final == "NEEDS_FIX"
        assert len(issues) == 1

    def test_rejected_takes_precedence_over_needs_fix(self):
        verdicts = [
            ReviewVerdict("functional", "REJECTED", issues=[
                ReviewIssue("critical", "api.ts", 1, "Missing endpoint", "Implement /users"),
            ]),
            ReviewVerdict("security", "NEEDS_FIX", issues=[
                ReviewIssue("major", "auth.ts", 5, "Weak hash", "Use bcrypt"),
            ]),
            ReviewVerdict("quality", "APPROVED"),
        ]
        final, issues = ReviewOrchestrator._aggregate_verdicts(verdicts)
        assert final == "REJECTED"
        assert len(issues) == 2


class TestContestedDetection:
    """Test ReviewOrchestrator._is_contested."""

    def test_unanimous_approved(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "APPROVED"),
            ReviewVerdict("quality", "APPROVED"),
        ]
        assert ReviewOrchestrator._is_contested(verdicts) is False

    def test_unanimous_rejected(self):
        verdicts = [
            ReviewVerdict("functional", "REJECTED"),
            ReviewVerdict("security", "REJECTED"),
            ReviewVerdict("quality", "REJECTED"),
        ]
        assert ReviewOrchestrator._is_contested(verdicts) is False

    def test_split_verdicts(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "REJECTED"),
            ReviewVerdict("quality", "APPROVED"),
        ]
        assert ReviewOrchestrator._is_contested(verdicts) is True

    def test_error_verdict_excluded(self):
        verdicts = [
            ReviewVerdict("functional", "APPROVED"),
            ReviewVerdict("security", "APPROVED", error="timeout"),
            ReviewVerdict("quality", "APPROVED"),
        ]
        # Only 2 non-error verdicts, both APPROVED → not contested
        assert ReviewOrchestrator._is_contested(verdicts) is False


class TestReviewerJsonParsing:
    """Test ReviewOrchestrator._parse_reviewer_json."""

    def _make_orchestrator(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")
        return ReviewOrchestrator(
            state_path=str(state_file),
            cwd=str(tmp_path),
            dry_run=True,
        )

    def test_parse_clean_json(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = json.dumps({
            "type": "functional",
            "verdict": "APPROVED",
            "issues": [],
            "summary": "All good",
        })
        result = orch._parse_reviewer_json(output, "functional")
        assert result.verdict == "APPROVED"
        assert result.issues == []
        assert result.summary == "All good"

    def test_parse_json_in_code_block(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = "Here is my review:\n```json\n" + json.dumps({
            "type": "security",
            "verdict": "REJECTED",
            "issues": [
                {"severity": "critical", "file": "db.ts", "line": 45,
                 "description": "SQL injection", "suggestion": "Parameterize"}
            ],
            "summary": "Critical security issue",
        }) + "\n```\nDone."
        result = orch._parse_reviewer_json(output, "security")
        assert result.verdict == "REJECTED"
        assert len(result.issues) == 1
        assert result.issues[0].severity == "critical"

    def test_parse_no_json(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        result = orch._parse_reviewer_json("No JSON here", "quality")
        assert result.verdict == "NEEDS_FIX"
        assert result.error is not None

    def test_parse_invalid_json(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        result = orch._parse_reviewer_json("{invalid json}", "quality")
        assert result.verdict == "NEEDS_FIX"
        assert result.error is not None

    def test_parse_invalid_verdict_defaults(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = json.dumps({"verdict": "UNKNOWN", "issues": [], "summary": ""})
        result = orch._parse_reviewer_json(output, "functional")
        assert result.verdict == "NEEDS_FIX"


class TestAdvisorJsonParsing:
    """Test ReviewOrchestrator._parse_advisor_json."""

    def _make_orchestrator(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")
        return ReviewOrchestrator(
            state_path=str(state_file),
            cwd=str(tmp_path),
            dry_run=True,
        )

    def test_parse_advisor_classifications(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = json.dumps([
            {"issue_index": 0, "classification": "GENUINE", "reasoning": "real bug"},
            {"issue_index": 1, "classification": "FALSE_POSITIVE", "reasoning": "style preference"},
        ])
        result = orch._parse_advisor_json(output, 2)
        assert result[0] == "GENUINE"
        assert result[1] == "FALSE_POSITIVE"
        assert result["0_reason"] == "real bug"
        assert result["1_reason"] == "style preference"

    def test_parse_advisor_wrapped(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = "```json\n" + json.dumps([
            {"issue_index": 0, "classification": "GENUINE", "reasoning": "valid concern"},
        ]) + "\n```"
        result = orch._parse_advisor_json(output, 1)
        assert result[0] == "GENUINE"

    def test_parse_advisor_no_json(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        result = orch._parse_advisor_json("I cannot provide that", 2)
        assert result == {}

    def test_parse_advisor_invalid_classification(self, tmp_path):
        orch = self._make_orchestrator(tmp_path)
        output = json.dumps([
            {"issue_index": 0, "classification": "MAYBE", "reasoning": "unsure"},
        ])
        result = orch._parse_advisor_json(output, 1)
        assert result[0] == "GENUINE"  # Invalid defaults to GENUINE (conservative)


class TestReviewIssue:
    """Test ReviewIssue serialization."""

    def test_to_dict_basic(self):
        issue = ReviewIssue("major", "auth.ts", 42, "No input validation", "Add Zod schema")
        d = issue.to_dict()
        assert d == {
            "severity": "major",
            "file": "auth.ts",
            "line": 42,
            "description": "No input validation",
            "suggestion": "Add Zod schema",
        }

    def test_to_dict_with_optional_fields(self):
        issue = ReviewIssue(
            "critical", "db.ts", 10, "SQL injection", "Parameterize",
            reviewer_type="security", owasp="A03",
        )
        d = issue.to_dict()
        assert d["reviewer_type"] == "security"
        assert d["owasp"] == "A03"


class TestReviewVerdict:
    """Test ReviewVerdict serialization."""

    def test_to_dict(self):
        verdict = ReviewVerdict(
            reviewer_type="functional",
            verdict="NEEDS_FIX",
            issues=[ReviewIssue("minor", "utils.ts", 5, "Dead code", "Remove")],
            summary="Minor issues found",
        )
        d = verdict.to_dict()
        assert d["type"] == "functional"
        assert d["verdict"] == "NEEDS_FIX"
        assert len(d["issues"]) == 1
        assert "timestamp" in d


class TestDryRun:
    """Test dry run output format."""

    def test_dry_run_output(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps({
            "config": {"advisor_enabled": True},
            "advisor": {"calls_made": 0, "max_calls": 3},
        }))

        orch = ReviewOrchestrator(
            state_path=str(state_file),
            cwd=str(tmp_path),
            dry_run=True,
        )
        output = orch._dry_run_output(["src/auth.ts", "src/db.ts"])
        data = json.loads(output)
        assert data["status"] == "dry_run"
        assert data["phase"] == "review"
        assert len(data["files_to_review"]) == 2
        assert set(data["reviewer_types"]) == set(REVIEWER_TYPES)
        assert data["advisor_available"] is True


class TestOutputFormat:
    """Test final JSON output format."""

    def test_success_output(self, tmp_path):
        state_file = tmp_path / "state.json"
        state_file.write_text("{}")

        orch = ReviewOrchestrator(
            state_path=str(state_file),
            cwd=str(tmp_path),
        )

        from review_orchestrator import RoundResult
        rounds = [
            RoundResult(
                round_num=1,
                verdicts=[
                    ReviewVerdict("functional", "APPROVED"),
                    ReviewVerdict("security", "APPROVED"),
                    ReviewVerdict("quality", "APPROVED"),
                ],
                final_verdict="APPROVED",
                issues_count=0,
            ),
        ]
        output = orch._output("success", rounds=rounds, total_s=12.5)
        data = json.loads(output)
        assert data["status"] == "success"
        assert data["phase"] == "review"
        assert data["final_verdict"] == "APPROVED"
        assert data["rounds_used"] == 1
        assert data["total_issues_found"] == 0
        assert data["total_time_s"] == 12.5
        assert data["advisor_used"] is False
