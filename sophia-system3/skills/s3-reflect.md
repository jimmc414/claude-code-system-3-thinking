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
