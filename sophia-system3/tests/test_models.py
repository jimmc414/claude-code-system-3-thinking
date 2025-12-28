"""
test_models.py - Tests for Pydantic models
"""

import pytest
from datetime import datetime
from uuid import uuid4

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from models import (
    SkillRecord, AgentState, SelfModel, AffectState, UserModel,
    Episode, SemanticRule, AuditResult, AgentResult
)


class TestSkillRecord:
    def test_defaults(self):
        record = SkillRecord()
        assert record.proficiency == 0.5
        assert record.experience_count == 0
        assert record.success_rate == 0.5

    def test_custom_values(self):
        record = SkillRecord(proficiency=0.8, experience_count=10, success_rate=0.9)
        assert record.proficiency == 0.8
        assert record.experience_count == 10


class TestAgentState:
    def test_defaults(self):
        state = AgentState()
        assert state.status == 'IDLE'
        assert state.active_goal is None
        assert state.tokens_used_session == 0

    def test_active_state(self):
        state = AgentState(status='ACTIVE', active_goal='Build feature')
        assert state.status == 'ACTIVE'
        assert state.active_goal == 'Build feature'


class TestSelfModel:
    def test_defaults(self):
        model = SelfModel()
        assert model.agent_id == "sophia-system3"
        assert len(model.terminal_creed) == 5
        assert model.total_sessions == 0

    def test_creed_immutable(self):
        model = SelfModel()
        assert "Prioritize user data safety" in model.terminal_creed[0]

    def test_capabilities(self):
        model = SelfModel(
            capabilities={"Python": SkillRecord(proficiency=0.9)}
        )
        assert model.capabilities["Python"].proficiency == 0.9


class TestEpisode:
    def test_creation(self):
        episode = Episode(
            id="ep_test_123",
            session_id="session_456",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            end_trigger="stop_hook"
        )
        assert episode.id == "ep_test_123"
        assert episode.outcome == "UNKNOWN"
        assert episode.trivial is False

    def test_with_heuristics(self):
        episode = Episode(
            id="ep_test",
            session_id="session",
            started_at=datetime.now(),
            ended_at=datetime.now(),
            end_trigger="stop_hook",
            heuristics=["Check logs first", "Verify config"],
            outcome="SUCCESS"
        )
        assert len(episode.heuristics) == 2
        assert episode.outcome == "SUCCESS"


class TestSemanticRule:
    def test_auto_id(self):
        rule = SemanticRule(
            trigger_concept="Docker",
            rule_content="Always check daemon status"
        )
        assert rule.id.startswith("rule_")
        assert rule.confidence == 0.8
        assert rule.source == "reflection"

    def test_manual_rule(self):
        rule = SemanticRule(
            trigger_concept="Database",
            rule_content="Use transactions for migrations",
            source="manual",
            confidence=0.9
        )
        assert rule.source == "manual"


class TestAuditResult:
    def test_pass(self):
        result = AuditResult(passed=True)
        assert result.passed is True
        assert result.risk_level == "low"

    def test_fail(self):
        result = AuditResult(
            passed=False,
            reason="Creed violation detected",
            risk_level="high",
            creed_violations=["Data safety compromised"]
        )
        assert result.passed is False
        assert len(result.creed_violations) == 1


class TestAgentResult:
    def test_complete(self):
        result = AgentResult(
            task_id="task_123",
            agent_type="s3-memory",
            status="complete",
            result={"matches": []}
        )
        assert result.status == "complete"
        assert result.error is None

    def test_error(self):
        result = AgentResult(
            task_id="task_456",
            agent_type="s3-reflection",
            status="error",
            error="Episode not found"
        )
        assert result.status == "error"
        assert result.error == "Episode not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
