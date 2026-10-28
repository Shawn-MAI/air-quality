# Quickstart Validation Guide: Project Foundation and Developer Environment

**Feature**: [spec.md](./spec.md) | **Contract**: [developer-interface.md](./contracts/developer-interface.md)

This guide proves the feature works end to end. The README quickstart (FR-011) must match these steps.

## Prerequisites

- macOS or Linux, or Windows with WSL2 running a Linux distribution (Clarification, Session 2026-10-28)
- Git
- Docker with Compose v2 (Docker Desktop on macOS, Docker Engine on Linux and WSL2). See [ADR-0001](../../../docs/adr/0001-local-stack-docker-compose.md).
- uv
- GNU Make

Exact minimum versions are set during implementation and recorded in the README.

## Scenario 1: Clean clone to running stack (User Story 1, SC-001, SC-002)

```bash
git clone <repository-url> air-quality
cd air-quality
cp .env.example .env
# Replace the placeholder passwords in .env
make up
```

**Expected**: `make up` exits `0`. `docker compose ps` shows the `db` service `healthy`. Total time under 15 minutes including installs for a new contributor, and under 5 minutes for `make up` once prerequisites are present.

## Scenario 2: Checks pass on the skeleton (User Story 2, SC-003)

```bash
make test
```

**Expected**: lint passes, then pytest passes, in under 2 minutes. Output names no failures.

## Scenario 3: Failures are clear (FR-005, FR-013)

1. Remove `APP_DB_USER` from `.env`, run `make up`. **Expected**: exit `1` with a message naming `APP_DB_USER`.
2. Restore it, then add a line with a lint violation to a Python file, run `make lint`. **Expected**: exit `1` with the file and line of the violation.
3. Stop the stack with `make down`, run `make test`. **Expected**: exit `1` with a message naming `make up`.

## Scenario 4: Stop keeps data; reset removes it (FR-003)

```bash
make up
# Create a marker table through the application role, for example:
# docker compose exec db psql -U airquality_app -d airquality -c "CREATE TABLE marker (id int);"
make down
make up
# Confirm the marker table still exists
make reset     # type "reset" when prompted
make up
# Confirm the marker table is gone
```

**Expected**: the marker survives `down` and `up`, and is gone after `reset` and `up`.

## Scenario 5: Secret and lint protection (User Story 3, SC-006)

1. Stage a file containing a fake key such as `AKIA` followed by 16 uppercase letters, and commit. **Expected**: the commit is blocked by gitleaks and names the file.
2. Stage a file with a ruff violation and commit. **Expected**: the commit is blocked by ruff.

## Scenario 6: Continuous integration (FR-006, SC-004)

Open a pull request with no changes beyond the skeleton. **Expected**: the `secrets` and `checks` jobs both pass, and the `checks` job log shows `make up` reporting healthy before `make test` runs.

## Evidence to record

Before the feature is marked complete, record in the README or the PR description: the verified prerequisite versions, the date, the OS used, and the timing for Scenario 1 and Scenario 2.
