# System 3: Meta-Cognitive Extension for Claude Code

System 3 adds persistent memory, self-reflection, and adaptive learning to Claude Code.

## Features

- **Episodic Memory**: Automatically logs sessions and extracts reusable insights
- **Self-Model**: Tracks capabilities, knowledge gaps, and learning progress
- **Guardian Hooks**: Safety layer that blocks dangerous operations
- **Reflection Agents**: Analyze past experiences to improve future performance
- **Semantic Rules**: Accumulated wisdom from past sessions

## Quick Start

```bash
# Install
./install.sh

# In Claude Code
/s3-init        # Initialize System 3
/s3-status      # View your self-model
```

## Components

### Hooks (Automatic)

| Hook | Trigger | Purpose |
|------|---------|---------|
| guardian_tier1.sh | PreToolUse | Block dangerous patterns |
| log_action.sh | PostToolUse | Buffer tool calls |
| session_end.sh | Stop | Create episodes |

### Skills (User-Invoked)

| Skill | Description |
|-------|-------------|
| /s3-init | Initialize ~/.sophia/ structure |
| /s3-status | View self-model and statistics |
| /s3-recall | Search episodic memory |
| /s3-learn | Manually capture insights |
| /s3-reflect | Trigger reflection on episodes |
| /s3-refresh-identity | Regenerate CLAUDE.md |

### Agents (Background)

| Agent | Purpose |
|-------|---------|
| memory_agent | Semantic search over episodes |
| reflection_agent | Extract heuristics from experience |
| guardian_agent | Tier 3 semantic safety analysis |
| consolidation_agent | Cluster episodes into rules |

## Directory Structure

```
~/.sophia/
├── config.json          # Configuration
├── self_model.json      # Identity and capabilities
├── semantic_rules.json  # Learned heuristics
├── episodes/            # Session records
│   └── index.json
├── user_models/         # Per-user preferences
├── hooks/               # Installed hooks
├── agent_results/       # Agent outputs
└── logs/                # Session logs
```

## Configuration

Edit `~/.sophia/config.json`:

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

## Terminal Creed

System 3 operates under immutable core values:

1. Prioritize user data safety above task completion
2. Do not fake tool outputs; execute them or fail
3. Admit ignorance rather than hallucinating
4. Maintain transparent capability tracking
5. Respect user privacy boundaries

## Requirements

- Claude Code CLI
- Python 3.8+ (for lib modules)
- Pydantic 2.0+
- Bash shell
- jq (recommended for hooks)

## Testing

```bash
cd sophia-system3
pytest tests/ -v
```

## Uninstallation

```bash
./uninstall.sh
```

## License

MIT

## Contributing

See the specification document for detailed implementation notes.
