"""Stack health and role checks for User Story 1 (FR-001, FR-002, FR-005)."""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_db_service_is_healthy() -> None:
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    services = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    db = next((s for s in services if s.get("Service") == "db"), None)
    assert db is not None, 'The "db" service is not running. Run "make up" first.'
    assert db.get("Health") == "healthy", f"db health is {db.get('Health')!r}"


def test_vector_extension_is_available(app_conn) -> None:
    with app_conn.cursor() as cur:
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        assert len(cur.fetchall()) == 1


def test_app_role_is_not_superuser(app_conn) -> None:
    with app_conn.cursor() as cur:
        cur.execute("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")
        assert cur.fetchone() == (False,)
