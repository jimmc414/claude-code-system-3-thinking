"""
locking.py - File locking utilities using directory-based locks

Protocol:
1. Acquire `{filename}.lock` (create directory exclusively)
2. Read current state
3. Modify
4. Write atomically (write to .tmp, rename)
5. Release lock (delete .lock directory)
6. Lock timeout: 5 seconds (stale lock = force acquire)
"""

import os
import time
import shutil
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


class LockAcquisitionError(Exception):
    """Raised when lock cannot be acquired within timeout."""
    pass


class FileLock:
    """
    Directory-based file lock for cross-process synchronization.

    Uses mkdir for atomic lock acquisition since it's guaranteed to be
    atomic on all filesystems.
    """

    def __init__(self, file_path: str, timeout: float = 5.0, poll_interval: float = 0.1):
        """
        Initialize a file lock.

        Args:
            file_path: Path to the file being protected
            timeout: Maximum seconds to wait for lock acquisition
            poll_interval: Seconds between lock acquisition attempts
        """
        self.file_path = Path(file_path)
        self.lock_path = Path(f"{file_path}.lock")
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._acquired = False

    def _is_lock_stale(self) -> bool:
        """Check if existing lock is stale (older than timeout)."""
        if not self.lock_path.exists():
            return False

        try:
            lock_mtime = self.lock_path.stat().st_mtime
            return (time.time() - lock_mtime) > self.timeout
        except OSError:
            # Lock was removed between exists() and stat()
            return True

    def _force_remove_stale_lock(self) -> bool:
        """Remove a stale lock. Returns True if removed."""
        try:
            shutil.rmtree(self.lock_path)
            return True
        except OSError:
            return False

    def acquire(self) -> bool:
        """
        Acquire the lock.

        Returns:
            True if lock acquired successfully

        Raises:
            LockAcquisitionError if timeout exceeded
        """
        start_time = time.time()

        while True:
            try:
                # mkdir is atomic - if it succeeds, we have the lock
                os.mkdir(self.lock_path)
                self._acquired = True
                return True
            except FileExistsError:
                # Lock exists - check if stale
                if self._is_lock_stale():
                    if self._force_remove_stale_lock():
                        continue  # Try again immediately

                # Check timeout
                elapsed = time.time() - start_time
                if elapsed >= self.timeout:
                    raise LockAcquisitionError(
                        f"Could not acquire lock for {self.file_path} "
                        f"after {self.timeout}s"
                    )

                # Wait before retry
                time.sleep(self.poll_interval)
            except OSError as e:
                raise LockAcquisitionError(
                    f"Error acquiring lock for {self.file_path}: {e}"
                )

    def release(self) -> None:
        """Release the lock by removing the lock directory."""
        if self._acquired and self.lock_path.exists():
            try:
                shutil.rmtree(self.lock_path)
            except OSError:
                pass  # Best effort removal
            finally:
                self._acquired = False

    def __enter__(self) -> 'FileLock':
        """Context manager entry - acquire lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - release lock."""
        self.release()


@contextmanager
def file_lock(file_path: str, timeout: float = 5.0):
    """
    Context manager for file locking.

    Usage:
        with file_lock("/path/to/file.json"):
            # read, modify, write file
            pass

    Args:
        file_path: Path to the file to lock
        timeout: Maximum seconds to wait for lock

    Yields:
        FileLock instance
    """
    lock = FileLock(file_path, timeout)
    try:
        lock.acquire()
        yield lock
    finally:
        lock.release()
