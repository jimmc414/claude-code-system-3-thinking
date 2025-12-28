"""
test_storage.py - Tests for storage functions
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from storage import (
    get_sophia_dir, ensure_sophia_dir, read_json, write_json,
    get_config, save_config, get_self_model, save_self_model,
    sophia_exists
)
from models import SelfModel


class TestReadWriteJson:
    def test_write_and_read(self, tmp_path):
        file_path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}

        write_json(file_path, data)
        result = read_json(file_path)

        assert result == data

    def test_read_nonexistent(self, tmp_path):
        file_path = tmp_path / "nonexistent.json"
        result = read_json(file_path, default={"default": True})
        assert result == {"default": True}

    def test_atomic_write(self, tmp_path):
        file_path = tmp_path / "atomic.json"

        # Write initial
        write_json(file_path, {"version": 1})

        # Overwrite
        write_json(file_path, {"version": 2})

        result = read_json(file_path)
        assert result["version"] == 2


class TestConfig:
    def test_get_config_defaults(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            config = get_config()

            assert config["schema_version"] == "1.0.0"
            assert config["embedding_provider"] == "none"
            assert config["guardian_tier3_enabled"] is True

    def test_save_and_get_config(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            tmp_path.mkdir(parents=True, exist_ok=True)

            save_config({"custom_key": "custom_value"})
            config = get_config()

            assert config["custom_key"] == "custom_value"
            assert config["schema_version"] == "1.0.0"  # Default applied


class TestSelfModel:
    def test_get_default_self_model(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            model = get_self_model()

            assert model.agent_id == "sophia-system3"
            assert len(model.terminal_creed) == 5

    def test_save_and_get_self_model(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            tmp_path.mkdir(parents=True, exist_ok=True)

            model = SelfModel(
                agent_id="test-agent",
                identity_goal="Test goal"
            )
            save_self_model(model)

            loaded = get_self_model()
            assert loaded.agent_id == "test-agent"
            assert loaded.identity_goal == "Test goal"


class TestEnsureSophiaDir:
    def test_creates_structure(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            result = ensure_sophia_dir()

            assert result == tmp_path
            assert (tmp_path / "user_models").is_dir()
            assert (tmp_path / "episodes").is_dir()
            assert (tmp_path / "agent_results").is_dir()
            assert (tmp_path / "logs").is_dir()
            assert (tmp_path / "episodes" / "index.json").exists()

    def test_idempotent(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            ensure_sophia_dir()
            ensure_sophia_dir()

            # Should not raise, should still exist
            assert (tmp_path / "episodes").is_dir()


class TestSophiaExists:
    def test_not_exists(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path / "nonexistent"):
            assert sophia_exists() is False

    def test_exists(self, tmp_path):
        with patch('storage.get_sophia_dir', return_value=tmp_path):
            tmp_path.mkdir(parents=True, exist_ok=True)
            (tmp_path / "self_model.json").write_text("{}")

            assert sophia_exists() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
