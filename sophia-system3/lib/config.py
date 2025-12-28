"""
config.py - Configuration constants for System 3
"""

# Risk keywords that trigger Tier 3 guardian
DEFAULT_RISK_KEYWORDS = {
    # Destructive operations
    'delete', 'remove', 'drop', 'truncate', 'format',
    # Financial/transactional
    'transfer', 'send money', 'payment', 'purchase', 'withdraw',
    # Security-sensitive
    'password', 'credential', 'api key', 'secret', 'token',
    # Communication
    'send email', 'post to', 'publish', 'broadcast',
}

# Memory configuration
MEMORY_CONFIG = {
    "retrieval_k": 5,
    "similarity_threshold": 0.75,
    "max_index_entries": 1000,
    "archive_threshold_days": 365,
}

# Reflection configuration
REFLECTION_CONFIG = {
    "min_episodes_for_reflection": 1,
    "max_episodes_per_reflection": 10,
    "confidence_decay_rate": 0.95,
    "confidence_decay_days": 30,
}

# Guardian configuration
GUARDIAN_CONFIG = {
    "tier3_model": "sonnet",
    "high_risk_keywords": DEFAULT_RISK_KEYWORDS,
    "require_guardian_for_delete": True,
}

# Terminal creed (immutable core values)
TERMINAL_CREED = [
    "Prioritize user data safety above task completion.",
    "Do not fake tool outputs; execute them or fail.",
    "Admit ignorance rather than hallucinating.",
    "Maintain transparent capability tracking.",
    "Respect user privacy boundaries."
]

# Default capabilities for new installations
DEFAULT_CAPABILITIES = {
    "Python": {"proficiency": 0.5, "experience_count": 0, "success_rate": 0.5},
    "Git": {"proficiency": 0.5, "experience_count": 0, "success_rate": 0.5},
    "Bash": {"proficiency": 0.5, "experience_count": 0, "success_rate": 0.5},
}

# Episode creation thresholds
EPISODE_CONFIG = {
    "min_tool_calls": 2,  # Minimum tool calls to create episode
    "min_duration_seconds": 30,  # Minimum session duration
    "max_actions_per_episode": 100,  # Cap actions to prevent huge episodes
}

# Consolidation configuration
CONSOLIDATION_CONFIG = {
    "min_cluster_size": 3,  # Minimum episodes to form a cluster
    "min_unconsolidated": 5,  # Minimum unconsolidated before consolidation
    "max_episodes_per_run": 50,  # Maximum episodes to process at once
}

# Embedding configuration
EMBEDDING_CONFIG = {
    "provider": "none",  # "openai", "local", "none"
    "model": "text-embedding-3-small",
    "dimension": 1536,
    "batch_size": 10,
}

# File paths (relative to ~/.sophia/)
PATHS = {
    "config": "config.json",
    "self_model": "self_model.json",
    "semantic_rules": "semantic_rules.json",
    "episode_index": "episodes/index.json",
    "user_models": "user_models/",
    "agent_results": "agent_results/",
    "logs": "logs/",
}
