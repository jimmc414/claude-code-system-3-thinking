# Sophia System 3

A persistent memory and self-model layer for Claude Code, based on the Sophia research paper.

## The Problem

Claude Code is stateless. Every session starts fresh with no memory of previous interactions. This means:

- You repeat the same instructions across sessions
- Claude makes the same mistakes it made last week
- No learning or improvement over time
- Preferences must be re-explained constantly
- Each session is isolated from all others

## What This Project Does

System 3 adds a persistence layer to Claude Code that maintains:

- **Episodic Memory**: Records of past interactions, what worked, what failed
- **Self-Model**: Claude's understanding of its own capabilities and limitations
- **Learned Heuristics**: Lessons extracted from experience ("always check Docker daemon before deploying")
- **User Model**: Remembered preferences and context about you

The result is a Claude Code that can reference past sessions, apply learned lessons, and improve over time.

## How It Works

Claude Code already provides tool execution (System 1) and reasoning (System 2). This project adds System 3 as an extension layer using Claude Code's native mechanisms:

```
Claude Code (existing)
├── Tools: Bash, Read, Write, Edit, etc.
└── Reasoning: Native chain-of-thought

System 3 Extension (this project)
├── Hooks: Capture actions automatically
├── Skills: User commands for memory access
├── Agents: Background processing for reflection
└── Storage: Persistent files in ~/.sophia/
```

### Components

**Hooks** (automatic, fast)
- `PreToolUse`: Safety checks before tool execution
- `PostToolUse`: Log actions to session buffer
- `Stop`: Commit episode when session ends

**Skills** (user-invoked)
- `/s3-init`: Set up the persistence layer
- `/s3-status`: View self-model and capabilities
- `/s3-recall`: Search past episodes
- `/s3-learn`: Manually capture an insight
- `/s3-reflect`: Trigger reflection on recent work

**Agents** (background processing)
- `s3-memory`: Semantic search over episodes
- `s3-reflection`: Extract heuristics from experiences
- `s3-guardian`: Validate high-risk actions
- `s3-consolidation`: Cluster similar episodes into rules

**Storage** (`~/.sophia/`)
```
~/.sophia/
├── self_model.json      # Identity, capabilities, knowledge gaps
├── episodes/            # Past interaction records
├── semantic_rules.json  # Consolidated heuristics
└── config.json          # User configuration
```

## Example

Without System 3:
```
Session 1:
  You: "Deploy to production"
  Claude: [Forgets to check Docker daemon, deployment fails]
  You: "Always check the daemon first"
  Claude: "Noted"

Session 2 (next week):
  You: "Deploy to production"
  Claude: [Makes the same mistake]
```

With System 3:
```
Session 2:
  You: "Deploy to production"
  Claude: [Retrieves relevant episode from memory]
  Claude: "Previous deployment failed because I didn't check the daemon.
           Checking that first..."
  [Proceeds correctly]
```

## Research Background

This implementation is based on:

**Sophia: A Persistent Agent Framework for Artificial Life**
Mingyang Sun, Feng Hong, Weinan Zhang
arXiv:2512.18202, December 2024

The paper introduces a "System 3" architecture that adds meta-cognitive capabilities to LLM agents:

- **Theory of Mind**: Modeling user beliefs and intentions
- **Episodic Memory**: Structured autobiographical records
- **Meta-Cognition**: Self-monitoring and self-improvement
- **Intrinsic Motivation**: Internal drives beyond task completion

Key findings from the paper:
- 80% reduction in reasoning steps for recurring tasks
- 40% improvement in success rate for complex tasks
- 24+ hours of continuous autonomous operation

The paper provides the theoretical framework. This project adapts those concepts to work as a Claude Code extension rather than a standalone agent.

### Differences from the Paper

The paper describes a complete agent architecture with custom System 1 (perception/action) and System 2 (reasoning) layers. This implementation takes a different approach:

| Paper Approach | This Implementation |
|----------------|---------------------|
| Custom tool execution | Use Claude Code's existing tools |
| Custom LLM reasoning loop | Use Claude's native reasoning |
| Event-driven async architecture | Hooks + skills + agents |
| Tree-of-thought search | Trust Claude's planning |
| Standalone Python application | Claude Code extension |

This reduces implementation complexity while preserving the core value: persistent memory and self-improvement.

## Current Status

**Planning phase.** The specification is being rewritten to reflect the Claude Code extension approach. Implementation has not yet begun.

Project files:
- `2512.18202v1.pdf` - The Sophia research paper
- `SPEC_REWRITE_PLAN.md` - Detailed implementation specification plan
- `system3_spec.md` - Original specification (being revised)
- `spec_evaluation.md` - Analysis of gaps in original spec

## Limitations

This is an experimental project with known constraints:

- **Not automatic**: Requires user to invoke skills; memory isn't magically consulted
- **Session-bound episodes**: One Claude Code session equals one episode
- **No real-time learning**: Reflection happens at session end or on demand
- **File-based storage**: Simple but not optimized for large scale
- **Embedding optional**: Works offline with keyword search; semantic search requires API or local model

## Requirements

- Claude Code CLI
- Python 3.11+
- Optional: OpenAI API key (for embeddings) or sentence-transformers (local embeddings)

## License

MIT

## References

- [Sophia: A Persistent Agent Framework for Artificial Life](https://arxiv.org/abs/2512.18202) (arXiv)
- [Claude Code](https://docs.anthropic.com/claude-code) (Anthropic)
