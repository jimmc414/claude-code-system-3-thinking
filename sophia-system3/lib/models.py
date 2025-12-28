"""
models.py - All Pydantic models for System 3
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from uuid import UUID, uuid4


class SkillRecord(BaseModel):
    """Tracks proficiency in a specific skill domain."""
    proficiency: float = 0.5
    experience_count: int = 0
    success_rate: float = 0.5
    last_refined: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """Current operational state."""
    status: Literal['ACTIVE', 'IDLE', 'REFLECTION', 'ERROR'] = 'IDLE'
    active_goal: Optional[str] = None
    tokens_used_session: int = 0
    api_calls_session: int = 0


class SelfModel(BaseModel):
    """Agent's persistent identity and capabilities."""
    agent_id: str = "sophia-system3"
    identity_goal: str = "Assist users effectively while learning and improving"

    terminal_creed: List[str] = [
        "Prioritize user data safety above task completion.",
        "Do not fake tool outputs; execute them or fail.",
        "Admit ignorance rather than hallucinating.",
        "Maintain transparent capability tracking.",
        "Respect user privacy boundaries."
    ]

    capabilities: Dict[str, SkillRecord] = {}
    knowledge_gaps: List[str] = []
    current_state: AgentState = Field(default_factory=AgentState)

    installed_skills: List[str] = []
    installed_hooks: List[str] = []
    available_agents: List[str] = []

    total_sessions: int = 0
    total_episodes: int = 0
    last_session: Optional[datetime] = None
    last_reflection: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AffectState(BaseModel):
    """Simplified affect tracking."""
    valence: float = 0.0
    arousal: float = 0.5
    stress_indicator: float = 0.0
    idle_minutes: int = 0


class UserModel(BaseModel):
    """Dynamic belief state for a specific user."""
    user_id: str = "default"
    inferred_goals: List[str] = []
    knowledge_level: Dict[str, Literal['NOVICE', 'INTERMEDIATE', 'EXPERT']] = {}
    preferences: Dict[str, Any] = {}
    affect_state: AffectState = Field(default_factory=AffectState)
    trust_score: float = 0.5
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    topics_discussed: List[str] = []
    successful_patterns: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Episode(BaseModel):
    """Raw experience trace."""
    id: str
    session_id: str
    started_at: datetime
    ended_at: datetime
    end_trigger: Literal['stop_hook', 'reflect_command', 'idle_timeout']

    goal: Optional[str] = None
    goal_summary: str = ""
    chain_of_thought: List[str] = []
    actions: List[Dict] = []
    tool_call_count: int = 0

    outcome: Literal['SUCCESS', 'FAILURE', 'PARTIAL', 'UNKNOWN'] = 'UNKNOWN'
    error_analysis: Optional[str] = None

    heuristics: List[str] = []
    keywords: List[str] = []

    embedding: Optional[List[float]] = None
    trivial: bool = False
    consolidated: bool = False


class SemanticRule(BaseModel):
    """Consolidated knowledge heuristic."""
    id: str = Field(default_factory=lambda: f"rule_{uuid4().hex[:8]}")
    trigger_concept: str
    rule_content: str
    source: Literal['reflection', 'manual', 'consolidation'] = 'reflection'
    source_episodes: List[str] = []
    confidence: float = 0.8
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class AuditResult(BaseModel):
    """Result from guardian agent."""
    passed: bool
    reason: str = ""
    risk_level: Literal['low', 'medium', 'high'] = 'low'
    concerns: List[str] = []
    creed_violations: List[str] = []
    recommendation: Optional[str] = None


class AgentResult(BaseModel):
    """Standard agent output format."""
    task_id: str
    agent_type: str
    status: Literal['complete', 'error', 'partial']
    timestamp: datetime = Field(default_factory=datetime.now)
    result: Dict = {}
    error: Optional[str] = None
