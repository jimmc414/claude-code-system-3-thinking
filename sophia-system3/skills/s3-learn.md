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
