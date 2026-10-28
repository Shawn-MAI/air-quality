"""Tooling configuration checks for User Story 2 (FR-004, FR-008)."""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_ruff_targets_python_312() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert data["tool"]["ruff"]["target-version"] == "py312"


def test_sqlfluff_uses_postgres_dialect() -> None:
    text = (REPO_ROOT / ".sqlfluff").read_text()
    assert "dialect = postgres" in text


def test_test_target_depends_on_lint_and_preflight() -> None:
    lines = (REPO_ROOT / "Makefile").read_text().splitlines()
    rule = next(line for line in lines if line.startswith("test:"))
    prerequisites = rule.split(":", 1)[1].split()
    assert "preflight" in prerequisites
    assert "lint" in prerequisites
