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

## Template Placeholders

- `{{IDENTITY_GOAL}}`: From self_model.identity_goal
- `{{TERMINAL_CREED}}`: Formatted numbered list from self_model.terminal_creed
- `{{CAPABILITIES_SUMMARY}}`: Markdown table of top 5 capabilities
- `{{KNOWLEDGE_GAPS}}`: Bullet list from self_model.knowledge_gaps
- `{{RECENT_HEURISTICS}}`: Last 10 rules from semantic_rules.json

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
