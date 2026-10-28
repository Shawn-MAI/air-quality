"""Fail-first tests for scripts/preflight.sh (FR-013)."""

import os
import secrets
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREFLIGHT = REPO_ROOT / "scripts" / "preflight.sh"

# Generated per run so no secret-like literal is committed.
GOOD_ENV = {
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "airquality",
    "POSTGRES_ADMIN_USER": "airquality_admin",
    "POSTGRES_ADMIN_PASSWORD": secrets.token_hex(16),
    "APP_DB_USER": "airquality_app",
    "APP_DB_PASSWORD": secrets.token_hex(16),
}


def _write_env(path: Path, values: dict[str, str]) -> Path:
    env_file = path / ".env"
    env_file.write_text("".join(f"{key}={value}\n" for key, value in values.items()))
    return env_file


def _run_preflight(env_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(PREFLIGHT)],
        capture_output=True,
        text=True,
        env={**os.environ, "ENV_FILE": str(env_file)},
        check=False,
    )


def test_missing_variable_fails_and_names_it(tmp_path: Path) -> None:
    values = {key: value for key, value in GOOD_ENV.items() if key != "APP_DB_USER"}
    result = _run_preflight(_write_env(tmp_path, values))

    assert result.returncode == 1
    assert "APP_DB_USER is not set in .env" in result.stdout + result.stderr


@pytest.mark.parametrize(
    ("secret", "placeholder"),
    [
        ("POSTGRES_ADMIN_PASSWORD", "change-me-admin"),
        ("APP_DB_PASSWORD", "change-me-app"),
    ],
)
def test_placeholder_secret_fails_and_names_it(
    tmp_path: Path, secret: str, placeholder: str
) -> None:
    values = {**GOOD_ENV, secret: placeholder}
    result = _run_preflight(_write_env(tmp_path, values))

    assert result.returncode == 1
    assert secret in result.stdout + result.stderr


def test_complete_environment_passes(tmp_path: Path) -> None:
    result = _run_preflight(_write_env(tmp_path, GOOD_ENV))

    assert result.returncode == 0, result.stdout + result.stderr
