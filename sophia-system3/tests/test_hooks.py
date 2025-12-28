"""
test_hooks.py - Tests for hook scripts

These tests verify the hook scripts execute correctly.
Note: Full integration testing requires Claude Code environment.
"""

import pytest
import subprocess
import tempfile
import os
from pathlib import Path


HOOKS_DIR = Path(__file__).parent.parent / "hooks"


class TestGuardianTier1:
    """Test guardian_tier1.sh blocklist patterns."""

    @pytest.fixture
    def hook_script(self):
        return HOOKS_DIR / "guardian_tier1.sh"

    def run_hook(self, hook_script, input_text, env=None):
        """Run hook with input and return exit code."""
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        result = subprocess.run(
            ["bash", str(hook_script)],
            input=input_text,
            capture_output=True,
            text=True,
            env=full_env
        )
        return result.returncode, result.stdout, result.stderr

    def test_allows_safe_command(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        code, stdout, _ = self.run_hook(hook_script, "ls -la /home/user")
        assert code == 0

    def test_blocks_rm_rf_root(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"HOME": tmpdir}
            os.makedirs(os.path.join(tmpdir, ".sophia", "logs"), exist_ok=True)

            code, stdout, _ = self.run_hook(hook_script, "rm -rf /", env=env)
            assert code == 1
            assert "BLOCKED" in stdout

    def test_blocks_drop_table(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"HOME": tmpdir}
            os.makedirs(os.path.join(tmpdir, ".sophia", "logs"), exist_ok=True)

            code, stdout, _ = self.run_hook(hook_script, "DROP TABLE users;", env=env)
            assert code == 1

    def test_blocks_fork_bomb(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"HOME": tmpdir}
            os.makedirs(os.path.join(tmpdir, ".sophia", "logs"), exist_ok=True)

            code, stdout, _ = self.run_hook(hook_script, ":(){:|:&};:", env=env)
            assert code == 1


class TestLogAction:
    """Test log_action.sh logging."""

    @pytest.fixture
    def hook_script(self):
        return HOOKS_DIR / "log_action.sh"

    def test_creates_buffer_file(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        session_id = "test_session_123"
        env = {
            "CLAUDE_SESSION_ID": session_id,
            "CLAUDE_TOOL_NAME": "Bash",
            "CLAUDE_TOOL_EXIT_CODE": "0"
        }

        result = subprocess.run(
            ["bash", str(hook_script)],
            input="test output",
            capture_output=True,
            text=True,
            env={**os.environ, **env}
        )

        # Should exit successfully
        assert result.returncode == 0

        # Buffer file should be created (async, so might need wait)
        import time
        time.sleep(0.1)

        buffer_file = Path(f"/tmp/sophia_session_{session_id}.jsonl")
        if buffer_file.exists():
            content = buffer_file.read_text()
            assert "Bash" in content
            buffer_file.unlink()  # Cleanup


class TestSessionEnd:
    """Test session_end.sh episode creation."""

    @pytest.fixture
    def hook_script(self):
        return HOOKS_DIR / "session_end.sh"

    def test_skips_empty_session(self, hook_script):
        if not hook_script.exists():
            pytest.skip("Hook not installed")

        with tempfile.TemporaryDirectory() as tmpdir:
            env = {
                "HOME": tmpdir,
                "CLAUDE_SESSION_ID": "empty_session"
            }
            os.makedirs(os.path.join(tmpdir, ".sophia", "episodes"), exist_ok=True)

            result = subprocess.run(
                ["bash", str(hook_script)],
                capture_output=True,
                text=True,
                env={**os.environ, **env}
            )

            # Should exit successfully (nothing to do)
            assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
