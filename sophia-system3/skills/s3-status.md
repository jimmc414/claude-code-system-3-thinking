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
