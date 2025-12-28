"""
storage.py - File I/O helpers for System 3 persistent state

All functions work with ~/.sophia/ directory structure.
Uses atomic writes and file locking for data integrity.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

from .locking import file_lock, LockAcquisitionError
from .models import SelfModel, Episode, SemanticRule


def get_sophia_dir() -> Path:
    """Get the ~/.sophia directory path."""
    return Path.home() / ".sophia"


def ensure_sophia_dir() -> Path:
    """
    Create the ~/.sophia directory structure if it doesn't exist.

    Structure:
        ~/.sophia/
        ├── config.json
        ├── self_model.json
        ├── user_models/
        ├── episodes/
        │   └── index.json
        ├── semantic_rules.json
        ├── agent_results/
        └── logs/

    Returns:
        Path to ~/.sophia directory
    """
    sophia_dir = get_sophia_dir()

    # Create subdirectories
    subdirs = [
        "",  # Root
        "user_models",
        "episodes",
        "agent_results",
        "logs",
        "hooks",  # For hook scripts
    ]

    for subdir in subdirs:
        (sophia_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Initialize empty episode index if needed
    index_path = sophia_dir / "episodes" / "index.json"
    if not index_path.exists():
        write_json(index_path, {
            "last_updated": datetime.now().isoformat(),
            "total_episodes": 0,
            "entries": []
        })

    # Initialize empty semantic rules if needed
    rules_path = sophia_dir / "semantic_rules.json"
    if not rules_path.exists():
        write_json(rules_path, [])

    return sophia_dir


def read_json(file_path: Path, default: Any = None) -> Any:
    """
    Read JSON from a file.

    Args:
        file_path: Path to the JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or default value
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return default

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def write_json(file_path: Path, data: Any, use_lock: bool = False) -> None:
    """
    Write JSON to a file atomically (write to temp, then rename).

    Args:
        file_path: Path to the JSON file
        data: Data to serialize
        use_lock: Whether to acquire a file lock first
    """
    file_path = Path(file_path)

    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    def do_write():
        # Write to temp file first
        fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            dir=file_path.parent
        )
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            # Atomic rename
            shutil.move(temp_path, file_path)
        except Exception:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    if use_lock:
        with file_lock(str(file_path)):
            do_write()
    else:
        do_write()


def get_config() -> Dict[str, Any]:
    """
    Get the current configuration.

    Returns:
        Configuration dict with defaults applied
    """
    config_path = get_sophia_dir() / "config.json"

    defaults = {
        "schema_version": "1.0.0",
        "embedding_provider": "none",
        "embedding_model": "text-embedding-3-small",
        "reflection_trigger": "manual",
        "guardian_tier3_enabled": True,
        "consolidation_min_episodes": 5,
        "user_mode": "single",
        "current_user": "default"
    }

    config = read_json(config_path, {})

    # Apply defaults for missing keys
    for key, value in defaults.items():
        if key not in config:
            config[key] = value

    return config


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config.json with locking.

    Args:
        config: Configuration dict to save
    """
    config_path = get_sophia_dir() / "config.json"
    write_json(config_path, config, use_lock=True)


def get_self_model() -> SelfModel:
    """
    Load the self model from disk.

    Returns:
        SelfModel instance (creates default if not exists)
    """
    model_path = get_sophia_dir() / "self_model.json"

    data = read_json(model_path)

    if data is None:
        return SelfModel()

    try:
        return SelfModel.model_validate(data)
    except Exception:
        # Invalid data, return default
        return SelfModel()


def save_self_model(model: SelfModel) -> None:
    """
    Save the self model to disk with locking.

    Args:
        model: SelfModel instance to save
    """
    model_path = get_sophia_dir() / "self_model.json"

    # Update timestamp
    model.updated_at = datetime.now()

    # Convert to dict for JSON serialization
    data = model.model_dump(mode='json')

    write_json(model_path, data, use_lock=True)


def get_episode_index() -> Dict[str, Any]:
    """
    Get the episode index.

    Returns:
        Episode index dict with entries list
    """
    index_path = get_sophia_dir() / "episodes" / "index.json"

    return read_json(index_path, {
        "last_updated": datetime.now().isoformat(),
        "total_episodes": 0,
        "entries": []
    })


def update_episode_index(entry: Dict[str, Any]) -> None:
    """
    Add an entry to the episode index with locking.

    Handles index capping (max 1000 entries).

    Args:
        entry: Episode index entry to add
    """
    index_path = get_sophia_dir() / "episodes" / "index.json"

    with file_lock(str(index_path)):
        index = read_json(index_path, {
            "last_updated": datetime.now().isoformat(),
            "total_episodes": 0,
            "entries": []
        })

        # Add new entry at beginning
        index["entries"].insert(0, entry)
        index["total_episodes"] = len(index["entries"])
        index["last_updated"] = datetime.now().isoformat()

        # Cap at 1000 entries
        if len(index["entries"]) > 1000:
            # Archive older entries
            year = datetime.now().year
            archive_path = get_sophia_dir() / "episodes" / f"index_archive_{year}.json"

            archived = index["entries"][1000:]
            existing_archive = read_json(archive_path, [])
            existing_archive.extend(archived)
            write_json(archive_path, existing_archive)

            index["entries"] = index["entries"][:1000]

        write_json(index_path, index)


def read_episode(episode_id: str) -> Optional[Episode]:
    """
    Read a full episode from disk.

    Args:
        episode_id: Episode ID to load

    Returns:
        Episode instance or None if not found
    """
    episode_path = get_sophia_dir() / "episodes" / f"{episode_id}.json"

    data = read_json(episode_path)

    if data is None:
        return None

    try:
        return Episode.model_validate(data)
    except Exception:
        return None


def write_episode(episode: Episode) -> None:
    """
    Write an episode to disk.

    Episodes are written once and don't need locking.

    Args:
        episode: Episode instance to save
    """
    episode_path = get_sophia_dir() / "episodes" / f"{episode.id}.json"

    data = episode.model_dump(mode='json')
    write_json(episode_path, data)


def get_semantic_rules() -> List[SemanticRule]:
    """
    Load all semantic rules.

    Returns:
        List of SemanticRule instances
    """
    rules_path = get_sophia_dir() / "semantic_rules.json"

    data = read_json(rules_path, [])

    rules = []
    for item in data:
        try:
            rules.append(SemanticRule.model_validate(item))
        except Exception:
            continue

    return rules


def add_semantic_rule(rule: SemanticRule) -> None:
    """
    Add a semantic rule with locking.

    Args:
        rule: SemanticRule to add
    """
    rules_path = get_sophia_dir() / "semantic_rules.json"

    with file_lock(str(rules_path)):
        data = read_json(rules_path, [])
        data.append(rule.model_dump(mode='json'))
        write_json(rules_path, data)


def save_semantic_rules(rules: List[SemanticRule]) -> None:
    """
    Save all semantic rules with locking.

    Args:
        rules: List of SemanticRule instances
    """
    rules_path = get_sophia_dir() / "semantic_rules.json"

    data = [r.model_dump(mode='json') for r in rules]
    write_json(rules_path, data, use_lock=True)


def get_user_model(user_id: str = "default") -> Optional[Dict[str, Any]]:
    """
    Load a user model.

    Args:
        user_id: User identifier

    Returns:
        User model dict or None
    """
    model_path = get_sophia_dir() / "user_models" / f"{user_id}.json"
    return read_json(model_path)


def save_user_model(user_id: str, model: Dict[str, Any]) -> None:
    """
    Save a user model.

    Args:
        user_id: User identifier
        model: User model dict
    """
    model_path = get_sophia_dir() / "user_models" / f"{user_id}.json"
    write_json(model_path, model)


def save_agent_result(task_id: str, result: Dict[str, Any]) -> None:
    """
    Save an agent result.

    Args:
        task_id: Task identifier
        result: Result dict to save
    """
    result_path = get_sophia_dir() / "agent_results" / f"{task_id}.json"
    write_json(result_path, result)


def read_agent_result(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Read an agent result.

    Args:
        task_id: Task identifier

    Returns:
        Result dict or None
    """
    result_path = get_sophia_dir() / "agent_results" / f"{task_id}.json"
    return read_json(result_path)


def sophia_exists() -> bool:
    """Check if ~/.sophia has been initialized."""
    sophia_dir = get_sophia_dir()
    return (
        sophia_dir.exists() and
        (sophia_dir / "self_model.json").exists()
    )
