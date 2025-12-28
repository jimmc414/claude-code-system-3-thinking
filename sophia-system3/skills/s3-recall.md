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
