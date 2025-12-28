# System 3: Meta-Cognitive Extension for Claude Code

System 3 adds persistent memory, self-reflection, and adaptive learning to Claude Code. It enables Claude to remember past sessions, learn from experience, and build an evolving understanding of its own capabilities.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Components](#components)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## Features

- **Episodic Memory**: Automatically logs sessions and creates searchable episode records
- **Self-Model**: Tracks capabilities, knowledge gaps, and learning progress over time
- **Guardian Hooks**: Three-tier safety layer that blocks dangerous operations
- **Reflection Agents**: Analyze past experiences to extract reusable heuristics
- **Semantic Rules**: Accumulated wisdom from past sessions, automatically applied
- **Identity Persistence**: CLAUDE.md template injection for consistent behavior

## Installation

### Prerequisites

- [Claude Code CLI](https://github.com/anthropics/claude-code) installed and configured
- Python 3.8+ with pip
- Bash shell (Linux/macOS/WSL)
- jq (recommended, for JSON processing in hooks)

### Install Dependencies

```bash
# Install Python dependencies
pip install pydantic>=2.0

# Optional: For semantic search with embeddings
pip install openai  # If using OpenAI embeddings
# or
pip install sentence-transformers  # For local embeddings
```

### Install System 3

```bash
# Clone or navigate to the repository
cd sophia-system3

# Make scripts executable
chmod +x install.sh uninstall.sh hooks/*.sh

# Run installation
./install.sh
```

The installer will:
1. Create `~/.sophia/` directory structure
2. Copy hooks to `~/.sophia/hooks/`
3. Copy skills to `~/.claude/skills/`
4. Initialize `config.json` and `self_model.json`
5. Configure Claude Code hooks in `~/.claude/hooks.json`

### Verify Installation

```bash
# Check files exist
ls -la ~/.sophia/
ls -la ~/.claude/skills/s3-*.md

# Check hooks configuration
cat ~/.claude/hooks.json
```

## Quick Start

```bash
# Start Claude Code
claude

# Initialize System 3 (first time only)
/s3-init

# Check your status
/s3-status
```

## Detailed Usage

### Skills Reference

#### `/s3-init` - Initialize System 3

Run once after installation to set up your identity and preferences.

```
/s3-init
```

This will:
- Create the `~/.sophia/` directory structure
- Initialize your self-model with default identity
- Set up empty episode index and semantic rules
- Optionally customize your identity goal and creed

#### `/s3-status` - View Self-Model

Display your current identity, capabilities, and statistics.

```
/s3-status
```

Output includes:
- Agent ID and identity goal
- Terminal creed values
- Capability proficiency levels
- Knowledge gaps
- Session and episode counts
- Recent episodes summary

#### `/s3-recall <query>` - Search Memory

Search your episodic memory for relevant past experiences.

```
/s3-recall "Docker deployment issues"
/s3-recall "authentication bug" --semantic=true
```

Parameters:
- `query` (required): What to search for
- `--semantic`: Use embedding-based search (requires embeddings configured)

Returns matched episodes ranked by relevance with:
- Episode ID and timestamp
- Goal summary
- Outcome (SUCCESS/FAILURE/PARTIAL)
- Extracted heuristics
- Relevance score

#### `/s3-learn <insight>` - Capture Knowledge

Manually save a heuristic or insight for future reference.

```
/s3-learn "Always check Docker daemon status before deployment" --domain="Docker"
/s3-learn "Use transactions for database migrations" --domain="Database"
```

Parameters:
- `insight` (required): The lesson to remember
- `--domain`: Category for the insight (optional)

#### `/s3-reflect` - Analyze Experiences

Trigger reflection on recent episodes to extract heuristics.

```
/s3-reflect                    # Reflect on last 5 episodes
/s3-reflect --recent=10        # Reflect on last 10 episodes
/s3-reflect --episode_id=ep_xxx  # Reflect on specific episode
```

This spawns the reflection agent which:
- Analyzes episode outcomes
- Extracts actionable heuristics
- Updates capability proficiency
- Identifies knowledge gaps

#### `/s3-refresh-identity` - Update CLAUDE.md

Regenerate your CLAUDE.md file from current self-model.

```
/s3-refresh-identity
```

Updates CLAUDE.md with:
- Current identity goal
- Terminal creed
- Top capabilities
- Knowledge gaps
- Recent heuristics

## Components

### Hooks (Automatic)

Hooks run automatically during Claude Code sessions.

| Hook | Trigger | Purpose | Latency |
|------|---------|---------|---------|
| `guardian_tier1.sh` | PreToolUse | Block dangerous regex patterns | <5ms |
| `log_action.sh` | PostToolUse | Buffer tool calls to temp file | <5ms |
| `session_end.sh` | Stop | Create episode from session | <500ms |

#### Guardian Tier 1 Blocklist

The guardian blocks these dangerous patterns:
- `rm -rf /` and variants
- `DROP TABLE`, `DROP DATABASE`
- SQL injection patterns (`; --`)
- Fork bombs (`:(){:|:&};:`)
- Disk operations (`mkfs`, `dd if=...of=/dev`)
- Unsafe permissions (`chmod 777`)

Blocked attempts are logged to `~/.sophia/logs/guardian_blocks.jsonl`.

### Skills (User-Invoked)

Skills are markdown-defined commands you invoke explicitly.

| Skill | File | Description |
|-------|------|-------------|
| `/s3-init` | `s3-init.md` | Initialize ~/.sophia/ structure |
| `/s3-status` | `s3-status.md` | View self-model and statistics |
| `/s3-recall` | `s3-recall.md` | Search episodic memory |
| `/s3-learn` | `s3-learn.md` | Manually capture insights |
| `/s3-reflect` | `s3-reflect.md` | Trigger reflection on episodes |
| `/s3-refresh-identity` | `s3-refresh-identity.md` | Regenerate CLAUDE.md |

### Agents (Background)

Agents are spawned for computationally intensive tasks.

| Agent | Purpose | Model | Background |
|-------|---------|-------|------------|
| `memory_agent` | Semantic search over episodes | haiku | Yes |
| `reflection_agent` | Extract heuristics from experience | sonnet | Yes |
| `guardian_agent` | Tier 3 semantic safety analysis | sonnet | Optional |
| `consolidation_agent` | Cluster episodes into rules | sonnet | Yes |

## Configuration

### config.json

Located at `~/.sophia/config.json`:

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

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `embedding_provider` | `"none"`, `"openai"`, `"local"` | `"none"` | Embedding source for semantic search |
| `reflection_trigger` | `"manual"`, `"on_session_end"` | `"manual"` | When to run reflection |
| `guardian_tier3_enabled` | `true`, `false` | `true` | Enable LLM-based safety review |
| `consolidation_min_episodes` | integer | `5` | Min episodes before consolidation |
| `user_mode` | `"single"`, `"multi"` | `"single"` | User identification mode |

### Enabling Embeddings

For semantic search with OpenAI:
```json
{
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small"
}
```
Requires `OPENAI_API_KEY` environment variable.

For local embeddings:
```json
{
  "embedding_provider": "local"
}
```
Requires `sentence-transformers` package installed.

## How It Works

### Session Lifecycle

1. **Session Start**: Claude reads `~/.sophia/self_model.json` and CLAUDE.md
2. **During Session**:
   - `guardian_tier1.sh` checks each tool use against blocklist
   - `log_action.sh` buffers tool calls to `/tmp/sophia_session_*.jsonl`
3. **Session End**:
   - `session_end.sh` reads buffer
   - Creates episode if significant (≥2 tool calls)
   - Updates session statistics
   - Optionally triggers reflection

### Episode Creation

Episodes capture:
- Session ID and timestamps
- Goal summary (inferred from actions)
- Tool calls with outcomes
- Extracted heuristics
- Keywords for search

Episodes are stored in `~/.sophia/episodes/{episode_id}.json` with an index at `~/.sophia/episodes/index.json`.

### Capability Tracking

The self-model tracks proficiency in domains:

```json
{
  "capabilities": {
    "Python": {
      "proficiency": 0.85,
      "experience_count": 47,
      "success_rate": 0.91
    },
    "Docker": {
      "proficiency": 0.68,
      "experience_count": 23,
      "success_rate": 0.78
    }
  }
}
```

Proficiency updates based on:
- Task outcomes (success/failure)
- Reflection analysis
- Manual feedback

### Semantic Rules

Heuristics are stored in `~/.sophia/semantic_rules.json`:

```json
[
  {
    "id": "rule_abc123",
    "trigger_concept": "Docker Deployment",
    "rule_content": "Always check daemon status before deploying",
    "source": "reflection",
    "confidence": 0.85,
    "source_episodes": ["ep_xxx", "ep_yyy"]
  }
]
```

Rules decay in confidence if not validated (5% per month).

## Examples

### Example 1: Learning from a Docker Deployment

```
# During a session, you help deploy a Docker container
# Session ends, episode ep_20241228_103000 is created

# Later, reflect on the experience
/s3-reflect --episode_id=ep_20241228_103000

# Output:
## Reflection Complete
### Heuristics Extracted: 1
1. **Docker Deployment**
   "Check container health status after deployment before marking complete"
   Confidence: 0.85
```

### Example 2: Searching Past Experiences

```
/s3-recall "SSL certificate configuration"

## Memory Search: "SSL certificate configuration"
### Matches Found: 2

1. **ep_20241225_140000** (3 days ago)
   - Goal: Configure SSL for nginx
   - Outcome: SUCCESS
   - Heuristics: "Use certbot for automatic renewal"
   - Relevance: 82%

2. **ep_20241220_091500** (8 days ago)
   - Goal: Debug SSL handshake failure
   - Outcome: PARTIAL
   - Relevance: 65%
```

### Example 3: Manual Knowledge Capture

```
/s3-learn "When debugging CORS issues, check both the server response headers and the browser's preflight request" --domain="API Development"

## Insight Captured
**Domain:** API Development
**Rule:** When debugging CORS issues, check both the server response headers and the browser's preflight request

Current semantic rules count: 12
```

## Directory Structure

```
~/.sophia/
├── config.json              # User configuration
├── self_model.json          # Identity, creed, capabilities
├── semantic_rules.json      # Learned heuristics
├── user_models/
│   └── default.json         # Per-user preferences
├── episodes/
│   ├── index.json           # Episode manifest
│   └── ep_*.json            # Individual episodes
├── hooks/
│   ├── guardian_tier1.sh
│   ├── log_action.sh
│   └── session_end.sh
├── agent_results/
│   └── {task_id}.json       # Agent outputs
└── logs/
    ├── guardian_blocks.jsonl # Blocked operations
    └── reflection_queue.txt  # Pending reflections
```

## Terminal Creed

System 3 operates under immutable core values that cannot be overridden:

1. **Prioritize user data safety above task completion**
2. **Do not fake tool outputs; execute them or fail**
3. **Admit ignorance rather than hallucinating**
4. **Maintain transparent capability tracking**
5. **Respect user privacy boundaries**

## Troubleshooting

### Hooks Not Running

1. Check hooks.json configuration:
   ```bash
   cat ~/.claude/hooks.json
   ```

2. Verify hooks are executable:
   ```bash
   chmod +x ~/.sophia/hooks/*.sh
   ```

3. Test hooks manually:
   ```bash
   echo "test" | ~/.sophia/hooks/guardian_tier1.sh
   echo $?  # Should be 0 for safe input
   ```

### Episodes Not Created

- Sessions with <2 tool calls are considered trivial and skipped
- Check if buffer file exists: `ls /tmp/sophia_session_*.jsonl`
- Verify jq is installed: `which jq`

### Embeddings Not Working

1. Check provider configuration in `~/.sophia/config.json`
2. For OpenAI: Verify `OPENAI_API_KEY` is set
3. For local: Install sentence-transformers: `pip install sentence-transformers`

### Permission Errors

```bash
# Fix permissions
chmod 755 ~/.sophia
chmod 644 ~/.sophia/*.json
chmod 755 ~/.sophia/hooks/*.sh
```

## Testing

```bash
cd sophia-system3

# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v
```

## Uninstallation

```bash
./uninstall.sh
```

This will:
1. Remove hooks from `~/.sophia/hooks/`
2. Remove skills from `~/.claude/skills/`
3. Optionally remove all data from `~/.sophia/`

To manually clean up:
```bash
rm -rf ~/.sophia/
rm -f ~/.claude/skills/s3-*.md
# Edit ~/.claude/hooks.json to remove System 3 entries
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code Session                      │
├─────────────────────────────────────────────────────────────┤
│  PreToolUse ──► guardian_tier1.sh (regex blocklist)         │
│       │                                                       │
│       ▼                                                       │
│  Tool Execution                                               │
│       │                                                       │
│       ▼                                                       │
│  PostToolUse ──► log_action.sh (buffer to /tmp)             │
│       │                                                       │
│       ▼                                                       │
│  Stop ──► session_end.sh (create episode)                   │
├─────────────────────────────────────────────────────────────┤
│  Skills (User-Invoked)                                       │
│  /s3-status, /s3-recall, /s3-learn, /s3-reflect             │
├─────────────────────────────────────────────────────────────┤
│  Agents (Background)                                         │
│  memory_agent, reflection_agent, guardian_agent              │
├─────────────────────────────────────────────────────────────┤
│  Persistent State (~/.sophia/)                               │
│  self_model.json, episodes/, semantic_rules.json             │
└─────────────────────────────────────────────────────────────┘
```

## License

MIT

## Contributing

See `system3_claude_code_spec.md` for the complete specification (2,811 lines) with detailed implementation notes.

## Acknowledgments

System 3 is inspired by cognitive science models of metacognition and episodic memory, adapted for AI agent self-improvement.
