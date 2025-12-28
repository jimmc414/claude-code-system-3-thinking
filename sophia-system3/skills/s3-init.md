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
