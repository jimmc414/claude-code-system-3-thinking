# System 3 Full Implementation Plan

**Status:** Phase 1 in progress (directory structure created)
**Date:** 2024-12-28
**Mode:** Continuous autonomous implementation

---

## Resume Prompt (Autonomous Mode)

```
Read implementation_plan.md and system3_claude_code_spec.md.

AUTONOMOUS IMPLEMENTATION MODE:
- Implement ALL 7 phases continuously without stopping for user confirmation
- Do NOT pause at checkpoints - proceed directly to the next phase
- Only stop if you encounter an unrecoverable error
- Use the todo list to track progress across context compactions
- Commit after completing each phase

Phase 1 directory structure exists at: /mnt/c/python/sophia/sophia-system3/

Execute phases in order:
1. Foundation: models.py, locking.py, storage.py, templates, install.sh, s3-init.md, s3-status.md
2. Hooks: guardian_tier1.sh, log_action.sh, session_end.sh
3. Memory: retrieval.py, s3-recall.md, memory_agent.md
4. Reflection: reflection_agent.md, s3-learn.md, s3-reflect.md
5. Guardian: guardian_agent.md, config.py
6. Consolidation: consolidation_agent.md
7. Polish: CLAUDE.md.template, s3-refresh-identity.md, embeddings.py, tests, README.md, uninstall.sh

Follow the spec EXACTLY. Create working code, not stubs.
Reference spec line numbers in the Key Spec References table below.
```

---

## Execution Rules

1. **No stopping** - Continue through all phases automatically
2. **Use spec line numbers** - Each component has exact spec references below
3. **Commit per phase** - Git commit after each phase completes
4. **Track via todos** - Update todo list so progress survives compaction
5. **Handle errors** - If something fails, fix it and continue (don't ask user)

---

## Project Structure (Created)

```
/mnt/c/python/sophia/sophia-system3/
├── hooks/          (empty - Phase 2)
├── skills/         (empty - Phase 1)
├── agents/         (empty - Phase 3+)
├── lib/            (empty - Phase 1)
├── templates/      (empty - Phase 1)
└── tests/          (empty - Phase 7)
```

---

## Implementation Phases

### Phase 1: Foundation (IN PROGRESS)
- [x] Create directory structure
- [ ] lib/models.py - All Pydantic models (spec lines 2625-2762)
- [ ] lib/locking.py - FileLock class with .lock directories
- [ ] lib/storage.py - read_json, write_json, get_self_model, etc.
- [ ] templates/config.json - Default configuration
- [ ] templates/self_model.json - Default self-model with creed
- [ ] install.sh - Installation script
- [ ] skills/s3-init.md - Bootstrap ~/.sophia/
- [ ] skills/s3-status.md - Display self-model

### Phase 2: Hooks
- [ ] hooks/guardian_tier1.sh (spec lines 678-732)
- [ ] hooks/log_action.sh (spec lines 735-773)
- [ ] hooks/session_end.sh (spec lines 776-891)
- [ ] Update install.sh for hooks

### Phase 3: Memory
- [ ] lib/retrieval.py - keyword_search, compute_retrieval_score
- [ ] Extend lib/storage.py for episodes
- [ ] skills/s3-recall.md (spec lines 1088-1162)
- [ ] agents/memory_agent.md (spec lines 1480-1600)

### Phase 4: Reflection
- [ ] agents/reflection_agent.md (spec lines 1602-1750)
- [ ] skills/s3-learn.md (spec lines 1164-1234)
- [ ] skills/s3-reflect.md (spec lines 1236-1330)
- [ ] Capability update logic

### Phase 5: Guardian
- [ ] agents/guardian_agent.md (spec lines 1752-1880)
- [ ] lib/config.py (spec lines 2764-2805)

### Phase 6: Consolidation
- [ ] agents/consolidation_agent.md (spec lines 1882-2000)

### Phase 7: Polish
- [ ] templates/CLAUDE.md.template (spec lines 2050-2150)
- [ ] skills/s3-refresh-identity.md (spec lines 1332-1400)
- [ ] lib/embeddings.py
- [ ] tests/
- [ ] README.md
- [ ] uninstall.sh

---

## Key Spec References

| Component | Spec Section | Lines |
|-----------|--------------|-------|
| Pydantic models | Appendix A | 2625-2762 |
| Config constants | Appendix B | 2764-2805 |
| guardian_tier1.sh | 8.1 | 678-732 |
| log_action.sh | 8.2 | 735-773 |
| session_end.sh | 8.3 | 776-891 |
| s3-init.md | 10.1 | 930-996 |
| s3-status.md | 10.2 | 998-1086 |
| s3-recall.md | 10.3 | 1088-1162 |
| s3-learn.md | 10.4 | 1164-1234 |
| s3-reflect.md | 10.5 | 1236-1330 |
| s3-refresh-identity.md | 10.6 | 1332-1400 |
| memory_agent.md | 12 | 1480-1600 |
| reflection_agent.md | 13 | 1602-1750 |
| guardian_agent.md | 14 | 1752-1880 |
| consolidation_agent.md | 15 | 1882-2000 |
| CLAUDE.md.template | 17 | 2050-2150 |
| install.sh | 20.2 | 2269-2333 |

---

## Files in Project

```
/mnt/c/python/sophia/
├── system3_claude_code_spec.md   # Main spec (2,811 lines) - THE SOURCE OF TRUTH
├── implementation_plan.md        # This file
├── README.md                     # GitHub readme
└── sophia-system3/               # Implementation directory
    ├── hooks/
    ├── skills/
    ├── agents/
    ├── lib/
    ├── templates/
    └── tests/
```

---

## After Compaction Checklist

If context was compacted, verify:
1. Read this file (implementation_plan.md)
2. Check which phases are marked [x] complete below
3. Check todo list for current progress
4. Continue from where you left off
5. Reference spec lines for each component

---

*Plan created: 2024-12-28*
*Updated: 2024-12-28 - Autonomous mode enabled*
