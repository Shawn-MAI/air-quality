"""Environment template checks for User Story 3 (FR-011, SC-005)."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_VARS = [
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_ADMIN_USER",
    "POSTGRES_ADMIN_PASSWORD",
    "APP_DB_USER",
    "APP_DB_PASSWORD",
]
SECRET_VARS = {
    "POSTGRES_ADMIN_PASSWORD": "change-me-admin",
    "APP_DB_PASSWORD": "change-me-app",
}


def _env_lines() -> list[str]:
    return (REPO_ROOT / ".env.example").read_text().splitlines()


def _values() -> dict[str, str]:
    return {
        key: value
        for key, value in (
            line.split("=", 1) for line in _env_lines() if re.match(r"^[A-Z_]+=", line)
        )
    }


def test_every_required_variable_is_documented() -> None:
    values = _values()
    missing = [name for name in REQUIRED_VARS if name not in values]
    assert not missing, f"Missing from .env.example: {missing}"


def test_every_variable_has_a_comment_above_it() -> None:
    lines = _env_lines()
    for index, line in enumerate(lines):
        if re.match(r"^[A-Z_]+=", line):
            assert index > 0 and lines[index - 1].startswith("#"), f"No comment above {line}"


def test_compose_references_are_all_in_env_example() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text()
    referenced = set(re.findall(r"\$\{([A-Z_]+)\}", compose))
    missing = referenced - set(_values())
    assert not missing, f"Compose uses variables missing from .env.example: {sorted(missing)}"


def test_secret_variables_use_placeholders_only() -> None:
    values = _values()
    for name, placeholder in SECRET_VARS.items():
        assert values[name] == placeholder, f"{name} must keep its placeholder value"
