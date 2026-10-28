"""Repository hygiene checks for User Story 3 (SC-005). These are guards, not fail-first tests."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )


def test_env_file_is_git_ignored() -> None:
    assert _git("check-ignore", "-q", ".env").returncode == 0


def test_env_file_is_not_tracked() -> None:
    result = _git("ls-files", ".env")
    assert result.returncode == 0
    assert result.stdout.strip() == ""
