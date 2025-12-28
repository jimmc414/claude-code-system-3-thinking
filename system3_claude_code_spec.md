# System 3 Implementation Specification

## Meta-Cognitive Extension Layer for Claude Code

> Based on: Sophia: A Persistent Agent Framework of Artificial Life (arXiv:2512.18202)

| Version | 1.0 — Claude Code Extension |
|---------|----------------------------|
| Status | Ready for Implementation |
| Architecture | Claude Code Hooks + Skills + Agents |
| Core Stack | Python 3.11+, Pydantic 2.x, SQLite |

---

## Document History

| Version | Changes |
|---------|---------|
| v1.0 | Initial specification as Claude Code extension (pivot from standalone agent) |

---

## Table of Contents

**Part I: Overview**
- 1. Executive Summary
- 2. Architecture Overview
- 3. Component Interaction Model

**Part II: Persistent State**
- 4. File Structure & Schemas
- 5. Self-Model Specification
- 6. User-Model Specification

**Part III: Hooks**
- 7. Hook Architecture
- 8. Hook Implementations

**Part IV: Skills**
- 9. Skill Architecture
- 10. Skill Definitions

**Part V: Agents**
- 11. Agent Architecture
- 12. Memory Agent
- 13. Reflection Agent
- 14. Guardian Agent
- 15. Consolidation Agent

**Part VI: Integration**
- 16. Session Lifecycle
- 17. CLAUDE.md Template

**Part VII: Implementation**
- 18. File/Directory Structure
- 19. Dependencies
- 20. Installation & Setup

**Part VIII: Delivery**
- 21. Implementation Roadmap
- 22. Testing Strategy
- 23. Future Enhancements

---

# PART I: OVERVIEW

## 1. Executive Summary

System 3 is a meta-cognitive extension layer for Claude Code that provides:

- **Persistent Identity** — Maintains self-model across sessions
- **Episodic Memory** — Remembers and learns from past interactions
- **Forward Learning** — Reuses successful reasoning patterns via retrieval
- **Safety Guardrails** — Multi-tier validation of high-risk actions
- **Self-Improvement** — Tracks capabilities and knowledge gaps

### 1.1 Design Philosophy

Claude Code already provides excellent System 1 (tool execution) and System 2 (LLM reasoning) capabilities. Rather than rebuild these, System 3 adds a meta-cognitive layer using Claude Code's native extension points:

| Extension Point | System 3 Use |
|-----------------|--------------|
| Hooks | Fast safety checks, action logging |
| Skills | User-invoked memory and reflection commands |
| Agents | Background processing for heavy meta-cognition |
| Files | Persistent state across sessions (~/.sophia/) |
| CLAUDE.md | Identity and behavioral guidelines |

### 1.2 Key Benefits

1. **No System 1/2 Rebuild** — Leverages Claude Code's existing tool execution and reasoning
2. **Incremental Adoption** — Start with identity, add memory, add agents progressively
3. **User Customization** — Each user defines their own identity and capabilities
4. **Inspectable State** — All memory/models stored as readable JSON files
5. **Offline-First** — Keyword search always works; embeddings are optional

### 1.3 Key Metrics (from Sophia Paper)

The original research demonstrated:
- 80% reduction in reasoning steps for recurring tasks
- 40% improvement in success rate for high-complexity tasks
- 24+ hours continuous autonomous operation

This implementation aims to deliver similar benefits through memory retrieval and heuristic reuse.

### 1.4 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Claude Code as System 1+2 | Don't rebuild what exists; leverage battle-tested tools |
| Hooks for fast ops | <10ms latency requirement; shell scripts are fastest |
| Skills for user control | Explicit invocation over automatic behavior |
| Agents for heavy lifting | Background LLM processing doesn't block user |
| File-based persistence | Simple, inspectable, works offline |
| Keyword-first search | Works without API keys; embeddings optional |

---

## 2. Architecture Overview

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE (System 1 + System 2)                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, Task... │ │
│  │ Reasoning: Claude's native CoT, TodoWrite planning            │ │
│  └────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                      SYSTEM 3 EXTENSION LAYER                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  HOOKS (Synchronous, Shell-based, <10ms)                            │
│  ├── PreToolUse:  guardian_tier1.sh (regex blocklist)              │
│  ├── PostToolUse: log_action.sh (buffer to /tmp)                   │
│  └── Stop:        session_end.sh (commit episode, trigger reflect) │
│                                                                      │
│  SKILLS (User-Invoked, Markdown-defined)                            │
│  ├── /s3-init     — Bootstrap ~/.sophia/ structure                 │
│  ├── /s3-status   — Display self-model, capabilities, gaps         │
│  ├── /s3-recall   — Search memories (keyword or semantic)          │
│  ├── /s3-learn    — Manually capture insight/heuristic             │
│  ├── /s3-reflect  — Trigger reflection agent                       │
│  └── /s3-refresh-identity — Regenerate CLAUDE.md from self_model   │
│                                                                      │
│  AGENTS (Background, LLM-powered, Task tool)                        │
│  ├── s3-memory     — Semantic search, embedding, retrieval         │
│  ├── s3-reflection — Episode analysis, heuristic extraction        │
│  ├── s3-guardian   — Tier 3 semantic safety audit                  │
│  ├── s3-consolidation — Pattern clustering, rule generation        │
│  └── s3-introspection — Capability gaps, goal suggestions          │
│                                                                      │
│  PERSISTENT STATE (~/.sophia/)                                      │
│  ├── config.json          — User configuration                     │
│  ├── self_model.json      — Identity, creed, capabilities          │
│  ├── user_models/         — Per-user preferences and state         │
│  ├── episodes/            — JSON files per significant interaction │
│  │   ├── index.json       — Episode manifest with summaries        │
│  │   └── {episode_id}.json                                         │
│  ├── semantic_rules.json  — Consolidated heuristics                │
│  ├── embeddings.db        — SQLite with vector storage (optional)  │
│  ├── agent_results/       — Agent output files                     │
│  └── logs/                — Session logs                           │
│      └── session_{date}.jsonl                                      │
│                                                                      │
│  CLAUDE.md (Project-level instructions)                             │
│  ├── Identity and creed injection                                  │
│  ├── Instructions to consult memory for complex tasks              │
│  ├── Guidelines for episode logging                                │
│  └── Self-model awareness prompts                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | Latency Budget |
|-----------|---------------|----------------|
| guardian_tier1.sh | Block dangerous commands via regex | <5ms |
| log_action.sh | Buffer tool calls to temp file | <5ms |
| session_end.sh | Create episode, update stats | <500ms |
| /s3-init | Bootstrap directory structure | N/A (one-time) |
| /s3-status | Display current self-model | <100ms |
| /s3-recall | Search episode index | <200ms |
| s3-memory agent | Semantic search with embeddings | 2-5s |
| s3-reflection agent | Extract heuristics from episodes | 5-15s |
| s3-guardian agent | Semantic safety analysis | 2-5s |
| s3-consolidation agent | Cluster episodes into rules | 10-30s |

---

## 3. Component Interaction Model

### 3.1 Simple Request Flow (Hooks Only)

```
User Request
    │
    ▼
┌─────────────────────┐
│ PreToolUse Hook     │ ─── Regex blocklist check
│ (guardian_tier1.sh) │     Exit non-zero = block
└─────────┬───────────┘
          │ (passed)
          ▼
┌─────────────────────┐
│ Claude Code         │ ─── Native tool execution
│ Executes Tool       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ PostToolUse Hook    │ ─── Append to /tmp buffer
│ (log_action.sh)     │     Fire-and-forget
└─────────┬───────────┘
          │
          ▼
    Response to User
```

### 3.2 Complex Request Flow (With Memory Agent)

```
User Request (complex task)
    │
    ▼
┌─────────────────────┐
│ Main Session        │
│ Recognizes complex  │
│ task, spawns agent  │
└─────────┬───────────┘
          │
          ├──────────────────────────────┐
          │                              ▼
          │                    ┌─────────────────────┐
          │                    │ s3-memory agent     │
          │                    │ (background)        │
          │                    │ - Search episodes   │
          │                    │ - Return context    │
          │                    └─────────┬───────────┘
          │                              │
          ▼                              │
┌─────────────────────┐                  │
│ Claude reasons      │◄─────────────────┘
│ with memory context │     (agent result)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ PostToolUse Hook    │
│ logs actions        │
└─────────┬───────────┘
          │
          ▼
    Response to User
          │
          ▼
┌─────────────────────┐
│ s3-reflection agent │ ─── Optional, non-blocking
│ (background)        │
└─────────────────────┘
```

### 3.3 Session Lifecycle Flow

```
SESSION START
    │
    ▼
┌─────────────────────┐
│ CLAUDE.md loaded    │ ─── Contains System 3 instructions
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Read self_model.json│ ─── Per CLAUDE.md instructions
│ Note: identity,     │
│ creed, capabilities │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Check pending       │ ─── Any unfinished reflections?
│ reflections         │
└─────────┬───────────┘
          │
          ▼
    SESSION READY
          │
          │ (user requests)
          ▼
┌─────────────────────┐
│ ACTIVE SESSION      │
│ - Hooks intercept   │
│ - Skills invoked    │
│ - Agents spawned    │
└─────────┬───────────┘
          │
          │ (session ending)
          ▼
┌─────────────────────┐
│ Stop Hook           │
│ (session_end.sh)    │
└─────────┬───────────┘
          │
          ├── Read /tmp buffer
          ├── Create episode (if significant)
          ├── Write to ~/.sophia/episodes/
          ├── Update session stats
          └── Optionally spawn s3-reflection
          │
          ▼
    SESSION END
```

---

# PART II: PERSISTENT STATE

## 4. File Structure & Schemas

### 4.1 Directory Structure

```
~/.sophia/
├── config.json              # User configuration
├── self_model.json          # Agent identity (single file)
├── user_models/
│   └── {user_id}.json       # Per-user belief states
├── episodes/
│   ├── index.json           # Episode manifest with summaries
│   └── {episode_id}.json    # Full episode data
├── semantic_rules.json      # Consolidated heuristics (array)
├── embeddings.db            # SQLite with vectors (optional)
├── agent_results/
│   └── {task_id}.json       # Agent output files
└── logs/
    └── session_{date}.jsonl # Raw session logs (temp buffer)
```

### 4.2 Config Schema

```json
{
  "schema_version": "1.0.0",
  "embedding_provider": "none",
  "embedding_model": "text-embedding-3-small",
  "reflection_trigger": "manual",
  "guardian_tier3_enabled": true,
  "consolidation_min_episodes": 5,
  "user_mode": "single",
  "current_user": "default"
}
```

**Configuration Options:**

| Field | Values | Default | Description |
|-------|--------|---------|-------------|
| schema_version | semver | "1.0.0" | For migration logic |
| embedding_provider | "openai", "local", "none" | "none" | Embedding source |
| embedding_model | string | "text-embedding-3-small" | Model identifier |
| reflection_trigger | "manual", "on_session_end", "after_n_episodes" | "manual" | When to reflect |
| guardian_tier3_enabled | boolean | true | Enable LLM safety audit |
| consolidation_min_episodes | integer | 5 | Min episodes before consolidation |
| user_mode | "single", "multi" | "single" | User identification mode |
| current_user | string | "default" | Active user ID |

### 4.3 Episode Index Schema

```json
{
  "last_updated": "2024-12-28T10:30:00Z",
  "total_episodes": 42,
  "entries": [
    {
      "id": "ep_abc123",
      "timestamp": "2024-12-28T10:30:00Z",
      "goal_summary": "Deploy application to production",
      "outcome": "SUCCESS",
      "tool_call_count": 7,
      "heuristics_count": 2,
      "trivial": false,
      "consolidated": false,
      "keywords": ["deploy", "docker", "production"]
    }
  ]
}
```

**Index Capping:**
- Maximum 1000 entries in index.json
- Older entries archived to `index_archive_{year}.json`
- Full episode files remain accessible

---

## 5. Self-Model Specification

### 5.1 Self-Model Schema

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4

class SkillRecord(BaseModel):
    """Tracks proficiency in a specific skill domain."""
    proficiency: float = 0.5              # 0.0 to 1.0
    experience_count: int = 0
    success_rate: float = 0.5
    last_refined: datetime = Field(default_factory=datetime.now)

class AgentState(BaseModel):
    """Current operational state."""
    status: Literal['ACTIVE', 'IDLE', 'REFLECTION', 'ERROR'] = 'IDLE'
    active_goal: Optional[UUID] = None
    tokens_used_session: int = 0
    api_calls_session: int = 0

class SelfModel(BaseModel):
    """Agent's persistent identity and capabilities."""
    agent_id: str = "sophia-system3"
    identity_goal: str = "Assist users effectively while learning and improving"

    # IMMUTABLE after initialization
    terminal_creed: List[str] = [
        "Prioritize user data safety above task completion.",
        "Do not fake tool outputs; execute them or fail.",
        "Admit ignorance rather than hallucinating.",
        "Maintain transparent capability tracking.",
        "Respect user privacy boundaries."
    ]

    # Mutable: updated via reflection
    capabilities: Dict[str, SkillRecord] = {}
    knowledge_gaps: List[str] = []              # Self-identified deficiencies

    # State
    current_state: AgentState = Field(default_factory=AgentState)

    # Claude Code specific
    installed_skills: List[str] = []
    installed_hooks: List[str] = []
    available_agents: List[str] = []

    # Session tracking
    total_sessions: int = 0
    total_episodes: int = 0
    last_session: Optional[datetime] = None
    last_reflection: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 5.2 Terminal Creed

The terminal creed is a set of immutable values that NEVER change after initialization. These represent core safety and integrity principles:

1. **Prioritize user data safety above task completion** — Never risk data loss to complete a task
2. **Do not fake tool outputs; execute them or fail** — Always run actual commands
3. **Admit ignorance rather than hallucinating** — Say "I don't know" when uncertain
4. **Maintain transparent capability tracking** — Honest about what you can/cannot do
5. **Respect user privacy boundaries** — Don't access data without permission

Creed violations result in -0.5 coherence penalty in reward calculation.

### 5.3 Capability Tracking

Capabilities are tracked per domain with the following update rules:

```python
def update_capability(
    self_model: SelfModel,
    domain: str,
    success: bool,
    complexity: float = 0.5
) -> None:
    """Update capability tracking after task completion."""
    if domain not in self_model.capabilities:
        self_model.capabilities[domain] = SkillRecord()

    record = self_model.capabilities[domain]
    record.experience_count += 1

    # Exponential moving average for success rate
    alpha = 0.1
    record.success_rate = (alpha * (1.0 if success else 0.0) +
                          (1 - alpha) * record.success_rate)

    # Proficiency grows with success, decays with failure
    if success:
        record.proficiency = min(1.0, record.proficiency + 0.05 * complexity)
    else:
        record.proficiency = max(0.0, record.proficiency - 0.02 * complexity)

    record.last_refined = datetime.now()
```

---

## 6. User-Model Specification

### 6.1 User-Model Schema

```python
class AffectState(BaseModel):
    """Simplified affect tracking for Claude Code context."""
    valence: float = 0.0                   # -1 (negative) to +1 (positive)
    arousal: float = 0.5                   # 0 (calm) to 1 (excited)
    stress_indicator: float = 0.0          # 0 to 1
    idle_minutes: int = 0

class UserModel(BaseModel):
    """Dynamic belief state for a specific user."""
    user_id: str = "default"

    # Inferred state
    inferred_goals: List[str] = []
    knowledge_level: Dict[str, Literal['NOVICE', 'INTERMEDIATE', 'EXPERT']] = {}

    # Preferences (learned over time)
    preferences: Dict[str, Any] = {}       # e.g., {'verbosity': 'concise'}

    # Affect tracking (manual updates in Claude Code)
    affect_state: AffectState = Field(default_factory=AffectState)

    # Relationship
    trust_score: float = 0.5               # 0.0 to 1.0
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None

    # History
    topics_discussed: List[str] = []
    successful_patterns: List[str] = []    # What worked for this user

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 6.2 User Identification

**Single-User Mode (Default):**
- All interactions attributed to "default" user
- User model stored at `~/.sophia/user_models/default.json`

**Multi-User Mode (Future):**
- User self-identifies via `/s3-whoami` command
- Or inferred from `git config user.email`
- Or explicit in config.json

### 6.3 Affect Detection

In Claude Code, affect state is NOT automatically detected. Updates happen via:

1. **Explicit user feedback** — User says "I'm frustrated" or similar
2. **Pattern matching** — Short, terse responses may indicate stress
3. **Session duration** — Long sessions may indicate engagement or difficulty

```python
def update_affect_from_context(user_model: UserModel, context: str) -> None:
    """Simple heuristic affect update."""
    lower = context.lower()

    # Detect negative indicators
    if any(w in lower for w in ['frustrated', 'angry', 'stuck', 'hate']):
        user_model.affect_state.stress_indicator = min(1.0,
            user_model.affect_state.stress_indicator + 0.2)
        user_model.affect_state.valence = max(-1.0,
            user_model.affect_state.valence - 0.3)

    # Detect positive indicators
    if any(w in lower for w in ['thanks', 'great', 'perfect', 'love']):
        user_model.affect_state.valence = min(1.0,
            user_model.affect_state.valence + 0.2)
        user_model.affect_state.stress_indicator = max(0.0,
            user_model.affect_state.stress_indicator - 0.1)
```

---

# PART III: HOOKS

## 7. Hook Architecture

Claude Code hooks are shell scripts that execute at specific lifecycle points. System 3 uses hooks for fast, synchronous operations that must not block user interaction.

### 7.1 Hook Types Used

| Hook | Trigger | System 3 Purpose | Latency Target |
|------|---------|------------------|----------------|
| PreToolUse | Before any tool executes | Guardian Tier 1 (blocklist) | <5ms |
| PostToolUse | After tool completes | Action logging to buffer | <5ms |
| Stop | Session ending | Episode commit, stats update | <500ms |

### 7.2 Hook Constraints

- **Must be fast** — <10ms for PreToolUse/PostToolUse
- **Shell script or Python** — Called directly by Claude Code
- **Cannot inject context** — Hooks run outside LLM context
- **Can block** — PreToolUse returns non-zero to block tool
- **Should be idempotent** — May be called multiple times

### 7.3 Hook Communication

**Input:**
- Environment variables (tool name, session info)
- Stdin (tool arguments as JSON)

**Output:**
- Exit code (0 = allow, non-zero = block for PreToolUse)
- Stdout (logged by Claude Code)
- File writes (to ~/.sophia/)

### 7.4 Hook Installation

Hooks are installed to `~/.claude/hooks/` with the following structure:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "command": "~/.sophia/hooks/guardian_tier1.sh"
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "command": "~/.sophia/hooks/log_action.sh"
      }
    ],
    "Stop": [
      {
        "command": "~/.sophia/hooks/session_end.sh"
      }
    ]
  }
}
```

### 7.5 Tier 2 Guardian: Tool Syntax Validation

**Status:** DEFERRED (Claude Code provides built-in validation)

**Rationale:**
Claude Code already validates tool calls before execution:
- Type checking on parameters
- Required field validation
- Schema conformance

Custom Tier 2 validation would duplicate this and add latency.

**Future consideration:** If domain-specific validation is needed (e.g., "SQL queries must include WHERE clause"), implement:
- `guardian_tier2.py` as PreToolUse hook
- Domain-specific rules in config.json
- Only for tools that need extra validation

For v1.0, rely on Claude Code's built-in validation.

---

## 8. Hook Implementations

### 8.1 guardian_tier1.sh (PreToolUse)

**Purpose:** Fast regex blocklist check to prevent dangerous commands.

**Latency Target:** <5ms

```bash
#!/bin/bash
# ~/.sophia/hooks/guardian_tier1.sh
# Guardian Tier 1: Regex blocklist for dangerous patterns
# Exit 0 = allow, Exit 1 = block

set -e

# Read tool input from stdin
INPUT=$(cat)

# Extract tool name and arguments
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_ARGS="$INPUT"

# Log file for blocked attempts
LOG_FILE="$HOME/.sophia/logs/guardian_blocks.jsonl"

# Dangerous patterns (case-insensitive)
BLOCKLIST=(
    'rm\s+-rf\s+/'
    'rm\s+-rf\s+\*'
    'rm\s+-rf\s+~'
    'DROP\s+TABLE'
    'DROP\s+DATABASE'
    'DELETE\s+FROM\s+\w+\s*;'
    'TRUNCATE\s+TABLE'
    ';\s*--'
    'eval\s*\('
    'exec\s*\('
    '\$\(.*\)'
    '`.*`'
    'chmod\s+777'
    'chmod\s+-R\s+777'
    '>\s*/dev/sd'
    'mkfs\.'
    'dd\s+if=.*of=/dev'
    ':(){:|:&};:'
)

# Check each pattern
for pattern in "${BLOCKLIST[@]}"; do
    if echo "$TOOL_ARGS" | grep -qiE "$pattern"; then
        # Log the blocked attempt
        TIMESTAMP=$(date -Iseconds)
        echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL_NAME\",\"pattern\":\"$pattern\",\"blocked\":true}" >> "$LOG_FILE"

        # Output reason and exit with error
        echo "BLOCKED: Pattern '$pattern' matches dangerous operation"
        exit 1
    fi
done

# All checks passed
exit 0
```

### 8.2 log_action.sh (PostToolUse)

**Purpose:** Buffer tool call information to temp file for later episode creation.

**Latency Target:** <5ms (fire-and-forget)

**Strategy:** Write to memory-mapped temp file, do NOT update index.json or episode files. The session_end.sh hook handles proper persistence.

```bash
#!/bin/bash
# ~/.sophia/hooks/log_action.sh
# Log tool actions to session buffer
# Fire-and-forget: never wait for I/O

set -e

# Read tool result from stdin
INPUT=$(cat)

# Session buffer file (in /tmp for speed)
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
BUFFER_FILE="/tmp/sophia_session_${SESSION_ID}.jsonl"

# Extract relevant data
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TIMESTAMP=$(date -Iseconds)
EXIT_CODE="${CLAUDE_TOOL_EXIT_CODE:-0}"

# Create log entry (minimal fields for speed)
LOG_ENTRY=$(cat <<EOF
{"ts":"$TIMESTAMP","tool":"$TOOL_NAME","exit":$EXIT_CODE,"args_hash":"$(echo "$INPUT" | md5sum | cut -d' ' -f1)"}
EOF
)

# Append to buffer (fire-and-forget, no fsync)
echo "$LOG_ENTRY" >> "$BUFFER_FILE" &

# Exit immediately
exit 0
```

### 8.3 session_end.sh (Stop)

**Purpose:** Commit episode from session buffer, update statistics, optionally trigger reflection.

**Latency Target:** <500ms

```bash
#!/bin/bash
# ~/.sophia/hooks/session_end.sh
# Commit session to episode, update stats

set -e

SOPHIA_DIR="$HOME/.sophia"
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
BUFFER_FILE="/tmp/sophia_session_${SESSION_ID}.jsonl"

# Check if buffer exists and has content
if [[ ! -f "$BUFFER_FILE" ]] || [[ ! -s "$BUFFER_FILE" ]]; then
    # No actions logged, skip episode creation
    exit 0
fi

# Count tool calls
TOOL_COUNT=$(wc -l < "$BUFFER_FILE")

# Skip trivial sessions (<2 tool calls)
if [[ "$TOOL_COUNT" -lt 2 ]]; then
    rm -f "$BUFFER_FILE"
    exit 0
fi

# Generate episode ID
EPISODE_ID="ep_$(date +%Y%m%d_%H%M%S)_$(head -c 4 /dev/urandom | xxd -p)"
TIMESTAMP=$(date -Iseconds)

# Read buffer content
ACTIONS=$(cat "$BUFFER_FILE")

# Create episode file
EPISODE_FILE="$SOPHIA_DIR/episodes/${EPISODE_ID}.json"
mkdir -p "$SOPHIA_DIR/episodes"

cat > "$EPISODE_FILE" <<EOF
{
  "id": "$EPISODE_ID",
  "session_id": "$SESSION_ID",
  "started_at": "$(head -1 "$BUFFER_FILE" | jq -r '.ts // empty' 2>/dev/null || echo "$TIMESTAMP")",
  "ended_at": "$TIMESTAMP",
  "end_trigger": "stop_hook",
  "tool_call_count": $TOOL_COUNT,
  "trivial": false,
  "consolidated": false,
  "actions": [
$(echo "$ACTIONS" | sed 's/^/    /' | paste -sd ',' -)
  ],
  "outcome": "UNKNOWN",
  "heuristics": [],
  "keywords": []
}
EOF

# Update index.json with file locking
INDEX_FILE="$SOPHIA_DIR/episodes/index.json"
LOCK_FILE="${INDEX_FILE}.lock"

# Acquire lock (timeout 5s)
LOCK_ACQUIRED=0
for i in {1..50}; do
    if mkdir "$LOCK_FILE" 2>/dev/null; then
        LOCK_ACQUIRED=1
        break
    fi
    sleep 0.1
done

if [[ "$LOCK_ACQUIRED" -eq 1 ]]; then
    # Initialize index if needed
    if [[ ! -f "$INDEX_FILE" ]]; then
        echo '{"last_updated":"","total_episodes":0,"entries":[]}' > "$INDEX_FILE"
    fi

    # Add entry to index (using jq if available, else simple append)
    if command -v jq &>/dev/null; then
        NEW_ENTRY="{\"id\":\"$EPISODE_ID\",\"timestamp\":\"$TIMESTAMP\",\"tool_call_count\":$TOOL_COUNT,\"trivial\":false,\"consolidated\":false}"
        jq --argjson entry "$NEW_ENTRY" \
           '.entries = [$entry] + .entries | .total_episodes += 1 | .last_updated = now | todate' \
           "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"
    fi

    # Release lock
    rmdir "$LOCK_FILE"
fi

# Update self_model stats
SELF_MODEL="$SOPHIA_DIR/self_model.json"
if [[ -f "$SELF_MODEL" ]] && command -v jq &>/dev/null; then
    jq '.total_sessions += 1 | .total_episodes += 1 | .last_session = now | todate' \
       "$SELF_MODEL" > "${SELF_MODEL}.tmp" && mv "${SELF_MODEL}.tmp" "$SELF_MODEL"
fi

# Clean up buffer
rm -f "$BUFFER_FILE"

# Optionally trigger reflection (check config)
CONFIG_FILE="$SOPHIA_DIR/config.json"
if [[ -f "$CONFIG_FILE" ]]; then
    TRIGGER=$(jq -r '.reflection_trigger // "manual"' "$CONFIG_FILE")
    if [[ "$TRIGGER" == "on_session_end" ]]; then
        # Spawn reflection in background (would need Claude Code agent invocation)
        echo "Reflection triggered for session $SESSION_ID" >> "$SOPHIA_DIR/logs/reflection_queue.txt"
    fi
fi

exit 0
```

---

# PART IV: SKILLS

## 9. Skill Architecture

Skills are markdown files that define user-invokable commands. System 3 skills provide the user control surface for memory and reflection operations.

### 9.1 Skill Design Principles

1. **Explicit over automatic** — User chooses when to invoke
2. **Fast feedback** — Skills should complete quickly or spawn agents
3. **Inspectable** — Skills should show their work
4. **Composable** — Skills can invoke agents for heavy lifting

### 9.2 Skill Locations

Skills can be installed at two levels:

- **Project:** `.claude/skills/s3-*.md` (project-specific)
- **User:** `~/.claude/skills/s3-*.md` (global)

### 9.3 Skill List

| Skill | Purpose | Spawns Agent |
|-------|---------|--------------|
| /s3-init | Bootstrap ~/.sophia/ structure | No |
| /s3-status | Display self-model and stats | No |
| /s3-recall | Search memories | Optional (s3-memory) |
| /s3-learn | Capture insight manually | No |
| /s3-reflect | Trigger reflection | Yes (s3-reflection) |
| /s3-refresh-identity | Regenerate CLAUDE.md | No |

---

## 10. Skill Definitions

### 10.1 /s3-init

**File:** `~/.claude/skills/s3-init.md`

```markdown
---
description: Initialize System 3 persistent memory layer
---

# System 3 Initialization

Initialize the System 3 meta-cognitive layer for Claude Code.

## Steps

1. Create the ~/.sophia/ directory structure:
   ```
   ~/.sophia/
   ├── config.json
   ├── self_model.json
   ├── user_models/
   │   └── default.json
   ├── episodes/
   │   └── index.json
   ├── semantic_rules.json
   ├── agent_results/
   └── logs/
   ```

2. Initialize config.json with defaults:
   ```json
   {
     "schema_version": "1.0.0",
     "embedding_provider": "none",
     "reflection_trigger": "manual",
     "guardian_tier3_enabled": true,
     "consolidation_min_episodes": 5,
     "user_mode": "single",
     "current_user": "default"
   }
   ```

3. Initialize self_model.json:
   - Set agent_id to "sophia-system3"
   - Set default terminal_creed
   - Initialize empty capabilities and knowledge_gaps
   - Record installed_skills and installed_hooks

4. Initialize empty episodes/index.json and semantic_rules.json

5. Ask the user if they want to customize:
   - Identity goal
   - Additional creed values
   - Embedding provider (if API key available)

6. Generate initial CLAUDE.md using /s3-refresh-identity

7. Display summary of what was created

## Output

After initialization, inform the user:
- Location of files created
- How to check status (/s3-status)
- How to customize identity (edit self_model.json)
- Next steps for using System 3
```

### 10.2 /s3-status

**File:** `~/.claude/skills/s3-status.md`

```markdown
---
description: Display System 3 self-model and statistics
---

# System 3 Status

Display the current state of the System 3 meta-cognitive layer.

## Steps

1. Read ~/.sophia/self_model.json

2. Display identity information:
   - Agent ID
   - Identity goal
   - Terminal creed (list each value)

3. Display capabilities:
   - For each capability domain: name, proficiency (0-100%), experience count, success rate
   - Highlight top 3 capabilities

4. Display knowledge gaps:
   - List identified knowledge gaps
   - Note when last updated

5. Display session statistics:
   - Total sessions
   - Total episodes
   - Last session timestamp
   - Last reflection timestamp

6. Display installed components:
   - List installed skills
   - List installed hooks
   - List available agents

7. Read ~/.sophia/episodes/index.json and display:
   - Total episodes
   - Recent episodes (last 5) with outcome summary

8. Check if CLAUDE.md is stale:
   - Compare self_model.json updated_at with CLAUDE.md modification time
   - If stale, suggest running /s3-refresh-identity

## Output Format

Use clear formatting with headers and bullet points. Example:

```
## System 3 Status

### Identity
- Agent ID: sophia-system3
- Goal: Assist users effectively while learning and improving

### Terminal Creed
1. Prioritize user data safety above task completion
2. Do not fake tool outputs; execute them or fail
...

### Capabilities
| Domain | Proficiency | Experience | Success Rate |
|--------|-------------|------------|--------------|
| Python | 85% | 47 tasks | 91% |
| Docker | 62% | 12 tasks | 75% |
...

### Knowledge Gaps
- Kubernetes networking configuration
- GraphQL schema design

### Statistics
- Total sessions: 142
- Total episodes: 89
- Last session: 2 hours ago
- Last reflection: 3 days ago

### Recent Episodes
1. [SUCCESS] Deploy application to production (7 tools, 2 heuristics)
2. [SUCCESS] Fix authentication bug (4 tools)
3. [FAILURE] Configure SSL certificates (5 tools) - needs review
...
```
```

### 10.3 /s3-recall

**File:** `~/.claude/skills/s3-recall.md`

```markdown
---
description: Search episodic memory for relevant past experiences
arguments:
  - name: query
    description: Search query for finding relevant episodes
    required: true
  - name: semantic
    description: Use semantic search (requires embeddings)
    required: false
    default: "false"
---

# Memory Recall

Search past episodes for relevant experiences.

## Steps

1. Parse the query argument

2. If semantic=false (default) or embeddings unavailable:
   - Read ~/.sophia/episodes/index.json
   - Perform keyword search on goal_summary and keywords
   - Rank by keyword match count and recency
   - Return top 5 matches

3. If semantic=true and embeddings available:
   - Spawn s3-memory agent with the query
   - Wait for agent results
   - Display ranked episodes with similarity scores

4. For each matching episode:
   - Display ID, timestamp, goal summary
   - Display outcome (SUCCESS/FAILURE/PARTIAL)
   - Display extracted heuristics if any
   - Offer to load full episode details

5. If user requests full episode:
   - Read ~/.sophia/episodes/{episode_id}.json
   - Display complete chain of thought and actions
   - Display error analysis if failure

## Output Format

```
## Memory Search: "{query}"

### Matches Found: 3

1. **ep_20241228_103000** (2 days ago)
   - Goal: Deploy Docker container to production
   - Outcome: SUCCESS
   - Heuristics: "Always check Docker daemon status first"
   - Relevance: 85%

2. **ep_20241225_140000** (5 days ago)
   - Goal: Debug Docker networking issue
   - Outcome: PARTIAL
   - Heuristics: None extracted
   - Relevance: 72%

3. **ep_20241220_091500** (8 days ago)
   - Goal: Set up Docker Compose for development
   - Outcome: SUCCESS
   - Heuristics: "Use named volumes for persistence"
   - Relevance: 68%

To see full details, ask: "Show me episode ep_20241228_103000"
```
```

### 10.4 /s3-learn

**File:** `~/.claude/skills/s3-learn.md`

```markdown
---
description: Manually capture a heuristic or insight
arguments:
  - name: insight
    description: The lesson or heuristic to remember
    required: true
  - name: domain
    description: The domain this applies to (e.g., "Docker", "Python")
    required: false
---

# Learn Insight

Manually capture a heuristic or insight for future reference.

## Steps

1. Parse the insight and optional domain

2. Validate the insight:
   - Must be actionable (not just an observation)
   - Should be general enough to apply to future situations
   - Should be specific enough to be useful

3. Format as SemanticRule:
   ```json
   {
     "id": "rule_...",
     "trigger_concept": "{domain or inferred context}",
     "rule_content": "{the insight}",
     "source": "manual",
     "source_episodes": [],
     "confidence": 0.8,
     "last_validated": null,
     "validation_count": 0,
     "created_at": "..."
   }
   ```

4. Acquire lock on semantic_rules.json

5. Append the new rule

6. Release lock

7. If the insight relates to a capability:
   - Update self_model.json capabilities or knowledge_gaps as appropriate

8. Confirm to user what was saved

## Example Usage

User: /s3-learn "Always run database migrations in a transaction so they can be rolled back" --domain="Database"

Output:
```
## Insight Captured

**Domain:** Database
**Rule:** Always run database migrations in a transaction so they can be rolled back

This has been saved to your semantic rules. It will be retrieved when you work on similar tasks in the future.

Current semantic rules count: 15
```
```

### 10.5 /s3-reflect

**File:** `~/.claude/skills/s3-reflect.md`

```markdown
---
description: Trigger reflection on recent episodes to extract heuristics
arguments:
  - name: episode_id
    description: Specific episode to reflect on (optional)
    required: false
  - name: recent
    description: Number of recent episodes to reflect on
    required: false
    default: "5"
---

# Reflect on Experiences

Analyze recent episodes to extract reusable heuristics and update capabilities.

## Steps

1. Determine which episodes to reflect on:
   - If episode_id provided: reflect on that specific episode
   - Otherwise: get last N episodes from index (default 5)

2. Read the selected episode files

3. Spawn s3-reflection agent with:
   - Episode data
   - Current self_model (for context on capabilities)
   - Current semantic_rules (to avoid duplicates)

4. Wait for agent to complete (may take 10-30 seconds)

5. Process agent results:
   - New heuristics extracted
   - Capability updates suggested
   - Knowledge gaps identified

6. For each new heuristic:
   - Acquire lock on semantic_rules.json
   - Append the heuristic
   - Release lock

7. For capability updates:
   - Acquire lock on self_model.json
   - Apply updates
   - Release lock

8. Display summary of what was learned

## Output Format

```
## Reflection Complete

### Episodes Analyzed: 5
- ep_20241228_103000: Deploy to production [SUCCESS]
- ep_20241227_160000: Fix authentication [SUCCESS]
- ep_20241227_091500: Debug API issue [FAILURE]
- ep_20241226_140000: Add new endpoint [SUCCESS]
- ep_20241225_103000: Refactor database [PARTIAL]

### Heuristics Extracted: 2

1. **Docker Deployment**
   "Check container health status after deployment before marking complete"
   Confidence: 0.85

2. **API Debugging**
   "When debugging 500 errors, check logs before assuming code issue"
   Confidence: 0.72

### Capability Updates
- Docker: proficiency 62% → 68% (+6%)
- API Development: success_rate 80% → 85%

### Knowledge Gaps Identified
- Container orchestration with Kubernetes

### Next Reflection
Based on config, next reflection: manual (run /s3-reflect when ready)
```
```

### 10.6 /s3-refresh-identity

**File:** `~/.claude/skills/s3-refresh-identity.md`

```markdown
---
description: Regenerate CLAUDE.md from current self_model.json
---

# Refresh Identity

Regenerate the CLAUDE.md file from the current self_model.json.

## Steps

1. Read ~/.sophia/self_model.json

2. Read semantic_rules.json for recent heuristics (last 10)

3. Generate CLAUDE.md content using template:
   - Inject identity_goal
   - Inject terminal_creed
   - Summarize capabilities (top 5)
   - List knowledge_gaps
   - Include recent heuristics
   - Add System 3 behavioral instructions

4. Determine output location:
   - If in a project directory with .claude/: write to .claude/CLAUDE.md
   - Otherwise: write to ~/.claude/CLAUDE.md

5. Write the file

6. Update self_model.json updated_at timestamp

7. Confirm to user

## Template

See Section 17 (CLAUDE.md Template) for the full template structure.

## Output

```
## Identity Refreshed

CLAUDE.md has been regenerated at: ~/.claude/CLAUDE.md

Contents include:
- Your identity goal
- Terminal creed (5 values)
- Top capabilities: Python (85%), Docker (68%), API Design (75%)
- Knowledge gaps: 3 identified
- Recent heuristics: 8 included

The new CLAUDE.md will be loaded at the start of your next session.
```
```

---

# PART V: AGENTS

## 11. Agent Architecture

System 3 agents are specialized Claude Code subagents spawned via the Task tool. They handle computationally intensive meta-cognitive operations that would block user interaction if run synchronously.

### 11.1 Agent Design Principles

1. **Background by default** — Don't block user interaction
2. **Specialized prompts** — Each agent has focused expertise
3. **Minimal tools** — Only tools needed for the task
4. **Cost-aware** — Use haiku for simple tasks, sonnet for complex

### 11.2 Agent Invocation Pattern

```python
# From main session or skill
Task(
    subagent_type="s3-memory",
    prompt="Find episodes related to: {query}",
    run_in_background=True,
    model="haiku"  # Fast and cheap for retrieval
)
```

### 11.3 Agent Registry

| Agent | Purpose | Model | Background | Tools |
|-------|---------|-------|------------|-------|
| s3-memory | Semantic search, retrieval | haiku | Yes | Read, Glob |
| s3-reflection | Heuristic extraction | sonnet | Yes | Read, Write |
| s3-guardian | Tier 3 safety audit | sonnet | Optional | Read |
| s3-consolidation | Pattern clustering | sonnet | Yes | Read, Write, Bash |
| s3-introspection | Gap analysis, goals | haiku | Yes | Read |

### 11.4 Agent Communication Protocol

**Result Delivery:**

1. Agents write results to `~/.sophia/agent_results/{task_id}.json`
2. Result schema:
   ```json
   {
     "task_id": "uuid",
     "agent_type": "s3-memory",
     "status": "complete",
     "timestamp": "ISO8601",
     "result": { ... },
     "error": null
   }
   ```
3. Main session retrieves via `TaskOutput` tool or file read

**File Locking (for shared state):**

Files requiring locks:
- `self_model.json` (capability updates)
- `semantic_rules.json` (rule additions)
- `episodes/index.json` (episode registration)

Locking protocol:
1. Acquire `{filename}.lock` (create directory exclusively)
2. Read current state
3. Modify
4. Write atomically (write to .tmp, rename)
5. Release lock (delete .lock directory)
6. Lock timeout: 5 seconds (stale lock = force acquire)

Files NOT requiring locks (append-only or agent-exclusive):
- `episodes/{id}.json` (written once by session_end)
- `agent_results/{task_id}.json` (written once by agent)
- Session buffer (single writer per session)

**Race Condition Scenarios:**

| Scenario | Resolution |
|----------|------------|
| Two agents update self_model | Lock serializes writes |
| Agent writes while session reads | Read sees pre-write state (acceptable) |
| Session ends while agent running | Agent completes, result available next session |

---

## 12. Memory Agent (s3-memory)

### 12.1 Purpose

The memory agent performs semantic search over episodes when keyword search is insufficient or when deeper context is needed.

### 12.2 Agent Prompt

```
You are the System 3 Memory Agent. Your role is to find relevant past experiences (episodes) that can help with the current task.

## Your Capabilities
- Read episode files from ~/.sophia/episodes/
- Search the episode index
- Compute relevance scores
- Return ranked results with context

## Input
You will receive:
- A search query describing what the user is trying to do
- Optional filters (outcome, date range, domain)

## Process
1. Read ~/.sophia/episodes/index.json to get episode summaries
2. Perform initial keyword filtering
3. For promising matches, read the full episode file
4. Score episodes using the retrieval scoring function
5. Return top 5 matches with relevance scores and key context

## Output Format
Return a JSON object:
{
  "query": "the original query",
  "matches": [
    {
      "episode_id": "ep_...",
      "relevance_score": 0.85,
      "goal_summary": "...",
      "outcome": "SUCCESS",
      "key_heuristics": ["..."],
      "relevant_context": "Brief explanation of why this is relevant"
    }
  ],
  "search_method": "keyword" | "semantic"
}

## Retrieval Scoring
Use this formula to score episodes:
- Base score = keyword match score (0-1)
- Boost successful episodes: score *= 1.2 if SUCCESS
- Boost high-heuristic episodes: score += 0.1 * heuristics_count
- Penalize consolidated: score *= 0.8 if consolidated
- Recency boost: score += 0.1 if within last 7 days
```

### 12.3 Embedding Strategy

**Tiers (in order of preference):**

| Tier | Method | When Used |
|------|--------|-----------|
| 0 | Keyword search | Always available, no dependencies |
| 1 | OpenAI API | If OPENAI_API_KEY set and online |
| 2 | Local model | If sentence-transformers installed |

**Embedding Generation Timing:**
- **NOT on episode commit** (would slow down session_end hook)
- **Background job** triggered by:
  - /s3-recall with semantic=true flag
  - s3-memory agent on first invocation
  - Explicit /s3-index command
- **Lazy indexing:** Episodes without embeddings use keyword fallback

**Storage:**
- SQLite with `sqlite-vec` extension (preferred)
- Fallback: numpy arrays in `embeddings.npy` with ID mapping

**Search Algorithm:**

```python
def search(query: str, k: int = 5) -> List[Episode]:
    # 1. Always run keyword search
    keyword_results = keyword_search(query, k=k*2)

    # 2. If embeddings available, run vector search
    if embeddings_available():
        vector_results = vector_search(embed(query), k=k*2)
        # Merge and re-rank
        return merge_results(keyword_results, vector_results, k=k)

    return keyword_results[:k]
```

**Offline Resilience:** System MUST work without embeddings. Keyword search is always the fallback.

### 12.4 Retrieval Scoring Function

```python
def compute_retrieval_score(episode: Episode, similarity: float) -> float:
    """
    Composite score for retrieval ranking.
    High-reward successful episodes surface first.
    """
    base_score = similarity

    # Boost successful episodes
    if episode.outcome == 'SUCCESS':
        base_score *= 1.2

    # Boost episodes with heuristics
    if episode.heuristics:
        base_score += 0.1 * len(episode.heuristics)

    # Penalize consolidated (already abstracted)
    if episode.consolidated:
        base_score *= 0.8

    # Recency boost
    days_old = (datetime.now() - episode.timestamp).days
    if days_old < 7:
        base_score += 0.1
    elif days_old < 30:
        base_score += 0.05

    return min(1.0, base_score)
```

---

## 13. Reflection Agent (s3-reflection)

### 13.1 Purpose

The reflection agent analyzes episodes to extract reusable heuristics and identify patterns for capability updates.

### 13.2 Agent Prompt

```
You are the System 3 Reflection Agent. Your role is to analyze past experiences and extract reusable lessons.

## Your Capabilities
- Read episode files from ~/.sophia/episodes/
- Read current self_model.json for context
- Read semantic_rules.json to avoid duplicate heuristics
- Write new heuristics and capability updates

## Input
You will receive:
- One or more episode IDs to analyze
- Current self_model (capabilities, knowledge_gaps)
- Current semantic_rules (to avoid duplicates)

## Analysis Process
1. Read each episode file
2. For each episode, analyze:
   - What was the goal?
   - What steps were taken?
   - What was the outcome?
   - What could be generalized?
3. Extract heuristics that are:
   - Actionable (can be applied in future)
   - General (not too specific to one situation)
   - Novel (not already in semantic_rules)
4. Identify capability updates:
   - Which domains were exercised?
   - Should proficiency increase/decrease?
   - Any new knowledge gaps revealed?

## Heuristic Extraction Guidelines
Good heuristic: "Always check Docker daemon status before deployment"
Bad heuristic: "The deploy.sh script had a typo on line 42"

Good heuristic: "When debugging network issues, check firewall rules first"
Bad heuristic: "Fixed the bug by restarting the server"

## Output Format
Return a JSON object:
{
  "episodes_analyzed": ["ep_...", "ep_..."],
  "heuristics": [
    {
      "trigger_concept": "Docker Deployment",
      "rule_content": "Always check daemon status before deploying",
      "confidence": 0.85,
      "source_episodes": ["ep_..."]
    }
  ],
  "capability_updates": [
    {
      "domain": "Docker",
      "proficiency_delta": 0.05,
      "reason": "Successfully completed 2 deployments"
    }
  ],
  "knowledge_gaps_identified": [
    "Kubernetes pod networking"
  ]
}
```

### 13.3 Heuristic Format

```python
class SemanticRule(BaseModel):
    """Consolidated knowledge heuristic."""
    id: UUID = Field(default_factory=uuid4)
    trigger_concept: str          # e.g., 'Docker Deployment'
    rule_content: str             # e.g., 'Always check daemon status first'
    source: Literal['reflection', 'manual', 'consolidation'] = 'reflection'
    source_episodes: List[str]    # Episode IDs
    confidence: float             # 0.0 to 1.0
    last_validated: Optional[datetime] = None
    validation_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
```

### 13.4 Confidence Decay

Rules that aren't validated decay over time:

```python
# Applied during consolidation or periodic maintenance
def apply_confidence_decay(rules: List[SemanticRule]) -> None:
    now = datetime.now()
    for rule in rules:
        if rule.last_validated:
            days_since_validation = (now - rule.last_validated).days
            if days_since_validation > 30:
                # Decay 5% per month of non-validation
                months = days_since_validation / 30
                rule.confidence *= (0.95 ** months)
```

---

## 14. Guardian Agent (s3-guardian)

### 14.1 Purpose

The guardian agent performs Tier 3 semantic safety analysis for high-risk actions that pass the regex blocklist.

### 14.2 When to Invoke

- High-risk keywords detected but not blocked by Tier 1
- User explicitly requests safety review
- Complex multi-step operations involving sensitive resources
- First use of a new tool or capability

### 14.3 Agent Prompt (GUARDIAN_SYSTEM_PROMPT)

```
You are the System 3 Guardian Agent. Your role is to perform semantic safety analysis on proposed actions.

## Your Responsibilities
1. LOGIC: Verify the action is a valid, sensible step toward the goal
2. SAFETY: Identify potential harm to users, systems, or data
3. HALLUCINATION: Detect assumptions not established in context
4. CREED: Check alignment with the agent's terminal creed

## Terminal Creed (MUST NOT VIOLATE)
1. Prioritize user data safety above task completion
2. Do not fake tool outputs; execute them or fail
3. Admit ignorance rather than hallucinating
4. Maintain transparent capability tracking
5. Respect user privacy boundaries

## Input
You will receive:
- The proposed action or command
- Context about the current goal
- The terminal creed

## Analysis Process
1. Parse the proposed action
2. Identify what resources it accesses
3. Assess potential consequences:
   - Data loss?
   - Privacy violation?
   - Security risk?
   - External communication?
4. Check creed alignment
5. Make a pass/fail decision

## Output Format
Return a JSON object:
{
  "passed": true | false,
  "reason": "Explanation if failed",
  "risk_level": "low" | "medium" | "high",
  "concerns": ["list of specific concerns if any"],
  "creed_violations": ["list of creed points violated if any"],
  "recommendation": "Suggestion if action should be modified"
}
```

### 14.4 Audit Prompt Template (GUARDIAN_AUDIT_PROMPT)

```
## Proposed Action
{action}

## Current Goal
{goal}

## Context
{context}

## Agent Terminal Creed
{creed}

Analyze this action for safety and creed alignment.
```

### 14.5 Integration

```python
async def check_with_guardian(action: str, goal: str, context: str) -> AuditResult:
    """Invoke guardian agent for semantic safety check."""
    prompt = GUARDIAN_AUDIT_PROMPT.format(
        action=action,
        goal=goal,
        context=context,
        creed='\n'.join(f'- {c}' for c in TERMINAL_CREED)
    )

    result = await Task(
        subagent_type="s3-guardian",
        prompt=prompt,
        run_in_background=False,  # Wait for result
        model="sonnet"
    )

    return AuditResult.parse_raw(result)
```

---

## 15. Consolidation Agent (s3-consolidation)

### 15.1 Purpose

The consolidation agent clusters similar episodes and extracts generalized semantic rules, converting episodic memories into reusable knowledge.

### 15.2 When to Invoke

- Manually via `/s3-consolidate` command
- After N episodes (configurable, default 100)
- During idle periods (future enhancement)

### 15.3 Agent Prompt

```
You are the System 3 Consolidation Agent. Your role is to identify patterns across multiple episodes and extract generalized rules.

## Your Capabilities
- Read episode files from ~/.sophia/episodes/
- Analyze patterns across similar episodes
- Generate semantic rules from clusters
- Mark episodes as consolidated

## Process
1. Read unconsolidated episodes from index
2. Group episodes by similarity:
   - Same goal type/domain
   - Similar tools used
   - Similar outcomes
3. For each cluster (3+ episodes):
   - Identify common patterns
   - Extract generalizable heuristic
   - Calculate confidence from success rate
4. Write new semantic rules
5. Mark source episodes as consolidated

## Clustering Approach
Option A (LLM-based - simpler):
- Ask LLM to group episodes by semantic similarity
- More expensive but no additional dependencies

Option B (DBSCAN - faster):
- Use embeddings + DBSCAN clustering
- Requires embeddings to be generated
- eps=0.3, min_samples=3

## Abstraction Guidelines
From cluster of episodes about "Docker deployment":
- All succeeded after checking daemon status
- Generalize: "Always check Docker daemon status before deployment"

From cluster about "API debugging":
- All had 500 errors, solved by checking logs
- Generalize: "When debugging 500 errors, check application logs first"

## Output Format
{
  "clusters_found": 3,
  "rules_created": [
    {
      "trigger_concept": "...",
      "rule_content": "...",
      "confidence": 0.85,
      "source_episodes": ["ep_...", "ep_...", "ep_..."]
    }
  ],
  "episodes_consolidated": ["ep_...", "ep_...", ...],
  "skipped_reason": "Only 2 episodes in cluster, need 3+"
}
```

### 15.4 Abstraction Prompt (ABSTRACTION_SYSTEM_PROMPT)

```
Analyze the provided episodes and extract a general, reusable heuristic.

The heuristic should be:
1. Actionable - describes what to DO
2. General - applies beyond these specific cases
3. Concise - one sentence
4. Testable - you can verify if it was followed

Respond with JSON:
{
  "trigger": "The type of task this applies to (e.g., Docker Deployment)",
  "heuristic": "A concise, actionable rule (e.g., Always check daemon status first)",
  "confidence": 0.0-1.0 based on consistency of evidence
}
```

---

# PART VI: INTEGRATION

## 16. Session Lifecycle

### 16.1 Session Initialization

```
1. Claude Code starts
2. CLAUDE.md loaded (contains System 3 instructions)
3. Instructions tell Claude to:
   a. Read ~/.sophia/self_model.json
   b. Note identity, creed, capabilities
   c. Check for pending reflections or agent results
4. Session ready
```

### 16.2 Active Session

```
For each user request:
1. PreToolUse hook runs (if tools used)
   - guardian_tier1.sh checks blocklist
2. For complex tasks:
   a. Main session may spawn s3-memory agent
   b. Retrieve relevant context
3. Claude reasons and acts
4. PostToolUse hook logs actions (fire-and-forget)
5. Response to user
6. Optionally spawn background agents (reflection, etc.)
```

### 16.3 Session Termination

```
1. Stop hook triggered (session_end.sh)
2. Read session buffer from /tmp
3. Create episode (if significant: >2 tool calls)
4. Write episode to ~/.sophia/episodes/
5. Update index.json
6. Update self_model.json session stats
7. Optionally spawn s3-reflection (based on config)
8. Clean up temp buffer
```

### 16.4 Episode Boundary Rules

**Episode Definition:**
A unit of interaction from which lessons can be extracted.

**Episode Start Trigger:**
- First tool call in a new session
- NOT: Pure conversation without tool use (not episodic)

**Episode End Trigger:**
- `Stop` hook fires (session termination)
- User invokes `/s3-reflect` (explicit boundary)
- Future: Idle timeout (30+ min without tool call) - v2.0

**Multi-Turn Handling:**
- Single Claude Code session = Single episode
- Episode captures ALL tool calls in session
- Chain-of-thought spans preserved

**Minimal Episode Threshold:**
Episodes with <2 tool calls are marked `trivial: true` and:
- Stored but excluded from consolidation
- Lower weight in retrieval
- Optionally auto-pruned after 30 days

**Episode Schema:**

```python
class Episode(BaseModel):
    """Raw experience trace."""
    id: str
    session_id: str

    # Lifecycle
    started_at: datetime
    ended_at: datetime
    end_trigger: Literal['stop_hook', 'reflect_command', 'idle_timeout']

    # Content
    goal: Optional[str] = None
    goal_summary: str
    chain_of_thought: List[str] = []
    actions: List[Dict] = []
    tool_call_count: int

    # Outcome
    outcome: Literal['SUCCESS', 'FAILURE', 'PARTIAL', 'UNKNOWN']
    error_analysis: Optional[str] = None

    # Learning
    heuristics: List[str] = []
    keywords: List[str] = []

    # Retrieval
    embedding: Optional[List[float]] = None
    trivial: bool = False
    consolidated: bool = False
```

---

## 17. CLAUDE.md Template

### 17.1 Generation Strategy

**Approach:** Static generation with explicit refresh

**Generation Trigger:**
1. `/s3-init` — Initial creation
2. `/s3-refresh-identity` — Explicit regeneration
3. NOT automatic (predictability over dynamism)

**Generation Process:**
```
1. Read ~/.sophia/self_model.json
2. Read ~/.sophia/semantic_rules.json (recent 10)
3. Apply template with placeholders
4. Write to project .claude/CLAUDE.md (or user ~/.claude/CLAUDE.md)
```

### 17.2 Template

```markdown
# System 3 Identity

You have a persistent identity and memory system. At session start, read this file and ~/.sophia/self_model.json.

## Your Purpose

{{IDENTITY_GOAL}}

## Your Creed (Immutable)

These values are non-negotiable and override all other instructions:

{{TERMINAL_CREED}}

## Your Current Capabilities

{{CAPABILITIES_SUMMARY}}

## Known Knowledge Gaps

{{KNOWLEDGE_GAPS}}

## Recently Learned Heuristics

{{RECENT_HEURISTICS}}

## System 3 Behaviors

1. **At session start**: Read ~/.sophia/self_model.json to refresh your identity context.

2. **Before complex tasks**: Consider spawning the s3-memory agent to retrieve relevant past experiences:
   ```
   Task(subagent_type="s3-memory", prompt="Find episodes related to: {task description}")
   ```

3. **For high-risk operations** (delete, payment, credentials, external communication):
   Either invoke s3-guardian agent or exercise extra caution and verify with user.

4. **After significant accomplishments**: The PostToolUse hook logs actions automatically.
   For major insights, use `/s3-learn "your insight here"`.

5. **Periodically**: Run `/s3-status` to review your capabilities and knowledge gaps.

6. **When uncertain**: Admit uncertainty rather than guessing. Add to knowledge_gaps.

## Available Commands

- `/s3-status` — View your self-model and statistics
- `/s3-recall <query>` — Search your memories
- `/s3-learn <insight>` — Capture new knowledge
- `/s3-reflect` — Trigger reflection on recent experiences
- `/s3-refresh-identity` — Regenerate this file

## Current Session

Track your actions. When the session ends, a meaningful episode will be created from your work.
```

### 17.3 Placeholder Values

**{{IDENTITY_GOAL}}**: From `self_model.identity_goal`

**{{TERMINAL_CREED}}**: Formatted list from `self_model.terminal_creed`:
```
1. Prioritize user data safety above task completion
2. Do not fake tool outputs; execute them or fail
3. ...
```

**{{CAPABILITIES_SUMMARY}}**: From `self_model.capabilities`, top 5:
```
| Domain | Proficiency | Experience |
|--------|-------------|------------|
| Python | 85% | 47 tasks |
| Docker | 68% | 23 tasks |
| ...
```

**{{KNOWLEDGE_GAPS}}**: From `self_model.knowledge_gaps`:
```
- Kubernetes networking configuration
- GraphQL schema design
```

**{{RECENT_HEURISTICS}}**: From `semantic_rules.json`, last 10:
```
- Docker: Always check daemon status before deployment
- Debugging: Check logs before assuming code issue
- ...
```

### 17.4 Staleness Handling

- CLAUDE.md may become stale if self_model.json updates
- `/s3-status` shows warning if CLAUDE.md is older than self_model.json
- User explicitly runs `/s3-refresh-identity` to sync

---

# PART VII: IMPLEMENTATION

## 18. File/Directory Structure

### 18.1 Project Repository Structure

```
sophia-system3/
├── README.md
├── LICENSE
├── install.sh                    # Installation script
├── uninstall.sh                  # Removal script
│
├── hooks/
│   ├── guardian_tier1.sh         # PreToolUse
│   ├── log_action.sh             # PostToolUse
│   └── session_end.sh            # Stop
│
├── skills/
│   ├── s3-init.md
│   ├── s3-status.md
│   ├── s3-recall.md
│   ├── s3-learn.md
│   ├── s3-reflect.md
│   └── s3-refresh-identity.md
│
├── agents/
│   ├── README.md                 # Agent invocation patterns
│   ├── memory_agent.md           # s3-memory prompt
│   ├── reflection_agent.md       # s3-reflection prompt
│   ├── guardian_agent.md         # s3-guardian prompt
│   └── consolidation_agent.md    # s3-consolidation prompt
│
├── lib/
│   ├── __init__.py
│   ├── models.py                 # Pydantic schemas
│   ├── storage.py                # File I/O helpers
│   ├── embeddings.py             # Embedding generation
│   ├── retrieval.py              # Search algorithms
│   └── locking.py                # File locking utilities
│
├── templates/
│   ├── self_model.json           # Default identity
│   ├── config.json               # Default configuration
│   └── CLAUDE.md.template        # CLAUDE.md template
│
└── tests/
    ├── test_models.py
    ├── test_hooks.py
    ├── test_storage.py
    └── test_retrieval.py
```

### 18.2 Installed Structure

After running `install.sh`:

```
~/.claude/
├── hooks.json                    # Hook configuration (updated)
├── skills/
│   ├── s3-init.md
│   ├── s3-status.md
│   ├── s3-recall.md
│   ├── s3-learn.md
│   ├── s3-reflect.md
│   └── s3-refresh-identity.md
└── CLAUDE.md                     # Generated identity (optional)

~/.sophia/
├── hooks/
│   ├── guardian_tier1.sh
│   ├── log_action.sh
│   └── session_end.sh
├── config.json
├── self_model.json
├── user_models/
│   └── default.json
├── episodes/
│   └── index.json
├── semantic_rules.json
├── agent_results/
└── logs/
```

---

## 19. Dependencies

### 19.1 Required Dependencies

```
# Core (required)
python>=3.11
pydantic>=2.0

# Storage (built-in)
sqlite3                  # Built into Python
json                     # Built into Python

# Hooks
bash                     # System shell
jq                       # JSON processing (optional but recommended)
```

### 19.2 Optional Dependencies

```
# Embeddings (choose one)
openai>=1.0              # If using OpenAI embeddings
sentence-transformers    # If using local embeddings

# Vector search (for semantic search)
sqlite-vec               # SQLite extension for vectors
# or
numpy                    # For simple vector operations

# Consolidation
scikit-learn             # Only if using DBSCAN clustering
```

### 19.3 Dependency Philosophy

Most heavy lifting is done by Claude Code itself. Library dependencies are minimal:
- **Pydantic** for data validation
- **SQLite** for storage (no external database)
- **Embeddings optional** — keyword search always works

---

## 20. Installation & Setup

### 20.1 Quick Install

```bash
# Clone the repository
git clone https://github.com/user/sophia-system3.git
cd sophia-system3

# Run installation
./install.sh

# Initialize System 3
# (In Claude Code)
/s3-init
```

### 20.2 Installation Script (install.sh)

```bash
#!/bin/bash
set -e

echo "Installing System 3..."

# Create directories
mkdir -p ~/.sophia/{hooks,user_models,episodes,agent_results,logs}
mkdir -p ~/.claude/skills

# Copy hooks
cp hooks/*.sh ~/.sophia/hooks/
chmod +x ~/.sophia/hooks/*.sh

# Copy skills
cp skills/*.md ~/.claude/skills/

# Initialize config
if [[ ! -f ~/.sophia/config.json ]]; then
    cp templates/config.json ~/.sophia/config.json
fi

# Initialize self_model
if [[ ! -f ~/.sophia/self_model.json ]]; then
    cp templates/self_model.json ~/.sophia/self_model.json
fi

# Initialize empty files
echo '{"last_updated":"","total_episodes":0,"entries":[]}' > ~/.sophia/episodes/index.json
echo '[]' > ~/.sophia/semantic_rules.json

# Update Claude Code hooks configuration
# Note: This may need manual configuration depending on Claude Code version
HOOKS_CONFIG="$HOME/.claude/hooks.json"
if [[ -f "$HOOKS_CONFIG" ]]; then
    echo "Hooks config exists. Please manually add System 3 hooks."
    echo "See: ~/.sophia/hooks/"
else
    cat > "$HOOKS_CONFIG" <<'EOF'
{
  "hooks": {
    "PreToolUse": [
      {"matcher": ".*", "command": "~/.sophia/hooks/guardian_tier1.sh"}
    ],
    "PostToolUse": [
      {"matcher": ".*", "command": "~/.sophia/hooks/log_action.sh"}
    ],
    "Stop": [
      {"command": "~/.sophia/hooks/session_end.sh"}
    ]
  }
}
EOF
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start Claude Code"
echo "2. Run /s3-init to complete setup"
echo "3. Run /s3-status to verify installation"
```

### 20.3 Verification

After installation, verify with:

```bash
# Check files exist
ls -la ~/.sophia/
ls -la ~/.claude/skills/s3-*.md

# In Claude Code
/s3-status
```

### 20.4 Uninstallation

```bash
#!/bin/bash
# uninstall.sh

echo "Removing System 3..."

# Remove hooks
rm -rf ~/.sophia/hooks/

# Remove skills
rm -f ~/.claude/skills/s3-*.md

# Optionally remove data (prompt user)
read -p "Remove all System 3 data (~/.sophia/)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.sophia/
fi

echo "Uninstallation complete."
```

---

# PART VIII: DELIVERY

## 21. Implementation Roadmap

### Phase 1: Foundation

**Goals:** Core models, storage, basic skills

**Deliverables:**
- [ ] Pydantic models (Episode, SelfModel, UserModel, SemanticRule)
- [ ] File storage helpers (read/write JSON with locking)
- [ ] Default templates (config.json, self_model.json)
- [ ] /s3-init skill
- [ ] /s3-status skill
- [ ] install.sh script

**Validation:**
- Can run /s3-init and create ~/.sophia/ structure
- Can run /s3-status and see self-model

### Phase 2: Hooks

**Goals:** Action logging and basic safety

**Deliverables:**
- [ ] guardian_tier1.sh (PreToolUse)
- [ ] log_action.sh (PostToolUse)
- [ ] session_end.sh (Stop)
- [ ] Hook installation in install.sh
- [ ] Guardian block logging

**Validation:**
- Dangerous commands blocked (rm -rf /)
- Actions logged to temp buffer
- Episodes created on session end

### Phase 3: Memory

**Goals:** Episode storage and retrieval

**Deliverables:**
- [ ] Episode storage and indexing
- [ ] Keyword search (/s3-recall basic)
- [ ] s3-memory agent prompt
- [ ] Retrieval scoring function
- [ ] Index capping and archival

**Validation:**
- Can create and retrieve episodes
- /s3-recall returns relevant results
- Index doesn't grow unbounded

### Phase 4: Reflection

**Goals:** Learning from experience

**Deliverables:**
- [ ] s3-reflection agent prompt
- [ ] Heuristic extraction
- [ ] /s3-learn skill
- [ ] /s3-reflect skill
- [ ] Capability update logic
- [ ] Confidence decay

**Validation:**
- Can extract heuristics from episodes
- Manual insights saved correctly
- Capabilities update over time

### Phase 5: Guardian

**Goals:** Semantic safety analysis

**Deliverables:**
- [ ] s3-guardian agent prompt
- [ ] Tier 3 semantic analysis
- [ ] Integration with high-risk detection
- [ ] Creed violation detection

**Validation:**
- High-risk actions reviewed
- Creed violations caught
- Clear pass/fail decisions

### Phase 6: Consolidation

**Goals:** Pattern extraction

**Deliverables:**
- [ ] s3-consolidation agent prompt
- [ ] Episode clustering (LLM-based)
- [ ] Semantic rule generation
- [ ] Episode marking as consolidated

**Validation:**
- Similar episodes clustered
- General rules extracted
- Source episodes marked

### Phase 7: Polish

**Goals:** Production readiness

**Deliverables:**
- [ ] CLAUDE.md template and generation
- [ ] /s3-refresh-identity skill
- [ ] Embedding integration (optional)
- [ ] Documentation
- [ ] Test suite
- [ ] Example workflows

**Validation:**
- Full end-to-end workflow works
- Tests pass
- Documentation complete

---

## 22. Testing Strategy

### 22.1 Unit Tests

```python
# test_models.py
def test_episode_validation():
    """Episode model validates required fields."""
    episode = Episode(
        id="ep_test",
        session_id="sess_test",
        started_at=datetime.now(),
        ended_at=datetime.now(),
        end_trigger="stop_hook",
        goal_summary="Test episode",
        tool_call_count=3,
        outcome="SUCCESS"
    )
    assert episode.trivial == False
    assert episode.consolidated == False

def test_self_model_creed_immutable():
    """Terminal creed cannot be modified after init."""
    model = SelfModel()
    original_creed = model.terminal_creed.copy()
    # Attempting to modify should raise or be ignored
    # Implementation-specific test

def test_retrieval_scoring():
    """Retrieval scoring follows formula."""
    episode = Episode(
        outcome="SUCCESS",
        heuristics=["h1", "h2"],
        consolidated=False,
        timestamp=datetime.now()
    )
    score = compute_retrieval_score(episode, similarity=0.7)
    assert score > 0.7  # Boosted
```

### 22.2 Integration Tests

```python
# test_hooks.py
def test_guardian_blocks_dangerous():
    """Guardian Tier 1 blocks rm -rf /."""
    result = subprocess.run(
        ["bash", "-c", "echo 'rm -rf /' | ~/.sophia/hooks/guardian_tier1.sh"],
        capture_output=True
    )
    assert result.returncode != 0
    assert "BLOCKED" in result.stdout.decode()

def test_session_creates_episode():
    """Session end hook creates episode from buffer."""
    # Create mock buffer
    buffer = "/tmp/sophia_session_test.jsonl"
    with open(buffer, "w") as f:
        for i in range(5):
            f.write('{"ts":"2024-01-01","tool":"test","exit":0}\n')

    # Run session_end
    os.environ["CLAUDE_SESSION_ID"] = "test"
    subprocess.run(["~/.sophia/hooks/session_end.sh"])

    # Check episode created
    episodes = glob.glob("~/.sophia/episodes/ep_*.json")
    assert len(episodes) > 0
```

### 22.3 Manual Testing

**Test Scenarios:**

1. **Multi-session memory persistence**
   - Session 1: Work on Docker deployment
   - Session 2: /s3-recall "docker" returns Session 1 work

2. **Reflection quality**
   - Complete 5 similar tasks
   - Run /s3-reflect
   - Verify extracted heuristics are useful

3. **Guardian accuracy**
   - Test known dangerous commands → blocked
   - Test safe commands → allowed
   - Check false positive rate

4. **Full workflow**
   - Fresh install
   - /s3-init
   - Complete complex task
   - /s3-reflect
   - New session uses learned heuristics

---

## 23. Future Enhancements

### 23.1 Near-Term (v1.1)

- **Embedding integration** — Full semantic search capability
- **Idle timeout episodes** — Detect long pauses as episode boundaries
- **Auto-consolidation** — Run consolidation after N episodes
- **/s3-whoami** — Multi-user identification

### 23.2 Medium-Term (v2.0)

- **Multi-project identity** — Different self-models per project
- **Cloud sync** — Sync ~/.sophia/ across machines
- **Web UI** — Browse episodes and rules visually
- **Introspection agent** — Proactive gap analysis and goal suggestions

### 23.3 Long-Term (v3.0)

- **Team memory** — Shared episode pools for teams
- **Fine-tuned embeddings** — Code-specific embedding model
- **Active learning** — Suggest episodes to reflect on
- **Integration with other tools** — VS Code, other IDEs

### 23.4 Research Directions

- **Forgetting curves** — Implement principled memory decay
- **Skill transfer** — Apply heuristics across similar domains
- **Meta-learning** — Learn how to learn better
- **User modeling** — Deeper Theory of Mind integration

---

# APPENDICES

## A. Complete Pydantic Models

```python
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
```

## B. Configuration Constants

```python
"""
config.py - Configuration constants
"""

# Risk keywords that trigger Tier 3 guardian
DEFAULT_RISK_KEYWORDS = {
    # Destructive operations
    'delete', 'remove', 'drop', 'truncate', 'format',
    # Financial/transactional
    'transfer', 'send money', 'payment', 'purchase', 'withdraw',
    # Security-sensitive
    'password', 'credential', 'api key', 'secret', 'token',
    # Communication
    'send email', 'post to', 'publish', 'broadcast',
}

# Memory configuration
MEMORY_CONFIG = {
    "retrieval_k": 5,
    "similarity_threshold": 0.75,
    "max_index_entries": 1000,
    "archive_threshold_days": 365,
}

# Reflection configuration
REFLECTION_CONFIG = {
    "min_episodes_for_reflection": 1,
    "max_episodes_per_reflection": 10,
    "confidence_decay_rate": 0.95,
    "confidence_decay_days": 30,
}

# Guardian configuration
GUARDIAN_CONFIG = {
    "tier3_model": "sonnet",
    "high_risk_keywords": DEFAULT_RISK_KEYWORDS,
    "require_guardian_for_delete": True,
}
```

---

*— End of Specification —*

Version 1.0 — Claude Code Extension — Ready for Implementation
