# Tasks: Project Foundation and Developer Environment

**Status**: Approved (2026-10-28)

**Input**: Design documents from `/specs/001-dev-env-foundation/`

**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/developer-interface.md](./contracts/developer-interface.md), [quickstart.md](./quickstart.md), [ADR-0001](../../docs/adr/0001-local-stack-docker-compose.md)

**Tests**: Included. Constitution Principle IV requires tests written first and failing first, so each story starts with failing tests. Every test task names the file it writes.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified on its own. User Story 2 and User Story 3 depend on the stack from User Story 1 for their end-to-end checks.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1, US2 or US3, mapped to the spec's user stories
- Paths are relative to the repository root

## Path Conventions

Single flat repository (see plan.md, Source Code). Infrastructure at the root, Python tooling in `pyproject.toml`, tests in `tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Tooling baseline and version control, required before any other work.

- [X] T001 Initialise the Git repository at the repository root and create branch `001-dev-env-foundation`. **Blocked until the user approves** (mandatory `before_constitution` hook; git is currently absent).
- [X] T002 Create `.python-version` at the repository root containing `3.12`
- [X] T003 Create `pyproject.toml` at the repository root with `requires-python = ">=3.12"`, a `dev` dependency group containing `pytest`, `ruff`, `sqlfluff`, `pre-commit`, and `psycopg[binary]`, and a `[tool.pytest.ini_options]` table with `testpaths = ["tests"]`
- [X] T004 Run `uv lock` in the repository root to create `uv.lock` (depends on T003)
- [X] T005 [P] Create `.gitignore` at the repository root excluding `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, and `.ruff_cache/`
- [X] T006 [P] Create `.sqlfluff` at the repository root with `[sqlfluff]` and `dialect = postgres`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared pieces that every story's commands use. No story work starts until this phase is complete.

**⚠️ CRITICAL**: The Makefile, preflight script, and test fixture are used by all three stories.

- [X] T007 [P] Create `.env.example` at the repository root listing every variable in the table below. Put a one-line purpose comment above each variable. Use these exact values:
  - `POSTGRES_PORT=5432`, purpose: host port for the data store
  - `POSTGRES_DB=airquality`, purpose: database name
  - `POSTGRES_ADMIN_USER=airquality_admin`, purpose: bootstrap superuser, used only by container initialisation
  - `POSTGRES_ADMIN_PASSWORD=change-me-admin`, purpose: bootstrap superuser password (placeholder; replace locally). Secret.
  - `APP_DB_USER=airquality_app`, purpose: non-superuser role used by the application and tests
  - `APP_DB_PASSWORD=change-me-app`, purpose: application role password (placeholder; replace locally). Secret.
  - Per data-model.md, the rule is: "Every variable above must be set and non-empty."
- [X] T008 Create `scripts/preflight.sh` (POSIX sh, executable). It must:
  - Check that `docker`, `docker compose` (v2), and `uv` are installed and meet the minimum versions. Define those minimums as named constants at the top of the script; their values are set in T020.
  - Check that `.env` exists and that each of the six variables from T007 is set and non-empty. Per data-model.md, the rule is: "Every variable above must be set and non-empty."
  - Fail (exit `1`) when a secret variable still equals its `.env.example` placeholder, and name the variable in the message.
  - Test first: write `tests/test_preflight.py` before the script. It runs `scripts/preflight.sh` against temporary `.env` files and covers (a) `APP_DB_USER` missing, expecting exit `1` and the message `APP_DB_USER is not set in .env`, and (b) a placeholder secret, expecting exit `1`. Both tests must fail before the script exists (Principle IV, FR-013).
  - Check that `POSTGRES_PORT` is free, unless the `db` service is already running (check with `docker compose ps`).
  - Print one line per problem that names it (for example `APP_DB_USER is not set in .env`), then exit `1`. Exit `0` when everything passes.
- [X] T009 Create `Makefile` at the repository root with `.PHONY` targets and a `preflight` target that runs `scripts/preflight.sh` (depends on T008). Leave `up`, `down`, `reset`, `lint`, and `test` for their story phases.
- [X] T010 Create `tests/conftest.py` (depends on T004). Provide a session fixture `app_conn` that connects with psycopg using `APP_DB_USER`, `APP_DB_PASSWORD`, `POSTGRES_DB`, and `POSTGRES_PORT` from the environment. When the connection fails, the fixture must fail with the message `Stack is not running. Run "make up" first.` (FR-013, FR-005).

**Checkpoint**: Makefile, preflight, and test fixture are in place.

- [X] T034 Gate before T014: confirm the current Docker Desktop licence terms for personal, non-commercial use, record the terms and date in `docs/adr/0001-local-stack-docker-compose.md`, and change its Status from `Proposed` to `Accepted`. If the terms do not allow the use, supersede the ADR and switch to a free alternative (ADR-0001). Story work that uses Docker (T014 onward) MUST NOT start until this task is done.

---

## Phase 3: User Story 1 - Start the Local Stack From a Clean Clone (Priority: P1) 🎯 MVP

**Goal**: One documented command starts a single pgvector-enabled data store, and the stop and reset commands work as specified.

**Independent Test**: On a machine with the prerequisites, copy `.env.example` to `.env`, run `make up`, and confirm the stack reports healthy and the vector capability is available (spec User Story 1, scenarios 1 to 4).

### Tests for User Story 1 (write first; must fail before T014 and T015)

> **NOTE: Run these tests before creating the compose file and init script. They must fail.**

- [X] T011 [US1] Create `tests/test_stack.py` with a test that runs `docker compose ps --format json` and asserts the `db` service reports `healthy` (User Story 1, scenario 1)
- [X] T012 [US1] Add a test to `tests/test_stack.py` that uses the `app_conn` fixture and asserts `SELECT extversion FROM pg_extension WHERE extname = 'vector'` returns one row (User Story 1, scenario 4)
- [X] T013 [US1] Add a test to `tests/test_stack.py` that uses the `app_conn` fixture and asserts `SELECT rolsuper FROM pg_roles WHERE rolname = current_user` returns `False` (plan Principle XII)

### Implementation for User Story 1

- [X] T014 [P] [US1] Create `docker-compose.yml` at the repository root with exactly one service, `db`:
  - Image `pgvector/pgvector:pg17`, pinned tag, never `latest` (research.md §2)
  - Environment from `.env` for `POSTGRES_DB`, `POSTGRES_USER` (from `POSTGRES_ADMIN_USER`), and `POSTGRES_PASSWORD` (from `POSTGRES_ADMIN_PASSWORD`)
  - Port mapping `${POSTGRES_PORT}:5432`
  - Named volume `pgdata` for `/var/lib/postgresql/data`
  - Mount `./db/init` read-only at `/docker-entrypoint-initdb.d`
  - Healthcheck with `CMD-SHELL` running `pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"`
  - No other services (FR-002)
- [X] T015 [P] [US1] Create `db/init/01-init.sh` (executable) for the first start on a fresh volume. It must enable the `vector` extension with `CREATE EXTENSION IF NOT EXISTS vector;`. It must also create the role named by `APP_DB_USER` as `NOSUPERUSER`, set its password from `APP_DB_PASSWORD`, and grant it `CONNECT` on `POSTGRES_DB`, plus `USAGE` and `CREATE` on schema `public`. Pass the names and password to `psql` with `-v` variables, not by string interpolation, so special characters are safe. The script must run again without error.
- [X] T016 [US1] Add the `up` target to `Makefile` (depends on T009, T014, T015). Steps, in order: `preflight`, `uv sync --frozen`, `docker compose up --wait`. The target must exit `0` when the `db` service is healthy and must not recreate the volume on a repeat run (contract `make up`, idempotent).
- [X] T017 [US1] Add the `down` target to `Makefile` that runs `docker compose down` with no volume flag, so data is kept (FR-003)
- [X] T018 [US1] Add the `reset` target to `Makefile`. It prints a warning, reads one line with `read -r`, and runs `docker compose down --volumes` only when the input is exactly `reset`. Any other input prints a cancellation message and exits `1` without changes (contract `make reset`)
- [X] T019 [US1] Verify User Story 1 from a stopped state: run `make up`, run `pytest tests/test_stack.py`, and confirm T011 to T013 pass. Then write a marker table as the app role, run `make down` and `make up`, and confirm the marker survives (quickstart Scenario 4, first half)
- [ ] T020 [US1] Confirm the minimum versions for Docker Compose v2 and uv: run `make up` with the oldest supported versions available to you. Set the constants in `scripts/preflight.sh` (T008) to the verified minimums. Record them in a comment at the top of the script so the README (T032) can quote them.

**Checkpoint**: User Story 1 works end to end. This is the MVP.

---

## Phase 4: User Story 2 - Run Quality Checks Locally With One Command (Priority: P2)

**Goal**: One command runs lint and the full test suite. The same checks run in CI on every change.

**Independent Test**: On a running stack, run `make test` and confirm lint and tests pass on the empty skeleton. Then confirm a deliberate lint violation makes it fail with a file location (spec User Story 2, scenarios 1 and 2).

### Tests for User Story 2 (write first; must fail before T022 and T023)

- [X] T021 [US2] Create `tests/test_tooling.py` with three checks: `pyproject.toml` sets `target-version = "py312"` under `[tool.ruff]`; `.sqlfluff` sets `dialect = postgres`; and the `test:` rule in `Makefile` lists `lint` as a prerequisite. Use `tomllib` for the TOML check and plain text parsing for the others. This test must fail before T022 and T023.

### Implementation for User Story 2

- [X] T022 [P] [US2] Add a `[tool.ruff]` section to `pyproject.toml` with `target-version = "py312"`, `line-length = 100`, and `[tool.ruff.lint]` `select = ["E", "F", "I", "UP", "B"]`. Edits are limited to the new section.
- [X] T023 [US2] Add the `lint` target to `Makefile` (depends on T006, T009, T022). It runs `uv run ruff check .`, then `uv run ruff format --check .`, then `uv run sqlfluff lint db/`. If `sqlfluff lint` exits non-zero when there are no `.sql` files yet, add a guard in the target that skips sqlfluff when no `.sql` files exist, and record the reason in a comment.
- [X] T024 [US2] Add the `test` target to `Makefile` (depends on T009, T010, T023). It declares `preflight` and `lint` as prerequisites, so a missing `.env` or placeholder secret is reported before tests run (FR-013), then runs `uv run --env-file .env pytest`. Its exit code is the exit code of the first failing step (FR-004).
- [X] T025 [US2] Create `.github/workflows/ci.yml` with one job named `checks`. The job runs on `pull_request` and on `push` to `main`. Steps, in order: checkout; install uv with a pinned `astral-sh/setup-uv` version; `cp .env.example .env`, then replace both secret placeholders with random values (for example `sed -i` with `openssl rand -hex 16`) so preflight passes; `make up` (this includes the healthy check through `docker compose up --wait`, FR-006); `make test`; `make down` with `if: always()`. Pin all third-party actions to a full commit SHA or a specific version tag (Principle XII).
- [X] T026 [US2] Verify the failure path: create a temporary Python file with an unused import in `tests/`, run `make test`, and confirm it exits `1` and names the file and line. Then delete the temporary file and confirm `make test` passes again (quickstart Scenario 3, second step)

**Checkpoint**: Lint and tests run with one command locally and in CI.

---

## Phase 5: User Story 3 - Configure the Environment Safely and Follow a Documented Workflow (Priority: P3)

**Goal**: Secrets stay out of version control, secrets are blocked at commit time and in CI, and the README documents the contributor workflow.

**Independent Test**: Copy `.env.example`, fill in values, start the stack with them, confirm `.env` does not appear in version control status, and confirm a staged fake secret is blocked (spec User Story 3, scenarios 1 to 3).

### Tests for User Story 3 (write first; must fail before T029 and T031)

- [X] T027 [US3] Create `tests/test_env_example.py` with three checks: (a) every variable from T007 appears in `.env.example`; (b) each variable is preceded by a comment line; (c) every `${VAR}` reference in `docker-compose.yml` appears in `.env.example` (SC-005). Only the placeholders `change-me-admin` and `change-me-app` may be used for the secret variables. This test must fail before T029 and before the secret checks are added.
- [X] T028 [US3] Create `tests/test_repo_hygiene.py` with a test that `git check-ignore -q .env` exits `0`, and a test that `git ls-files` does not list `.env` (SC-005). This test requires T001 and T005. It is a guard rather than a fail-first test: confirm it fails when the `.env` line is temporarily removed from `.gitignore`, then restore the line.

### Implementation for User Story 3

- [X] T029 [P] [US3] Create `.pre-commit-config.yaml` at the repository root with three pinned hooks: ruff (`check` and `format`), sqlfluff lint for `.sql` files, and gitleaks (`protect --staged`). Pin each repo to a specific revision (FR-010, SC-006).
- [X] T030 [US3] Add an install step to the `up` target in `Makefile` (depends on T016, T029). It runs `uv run pre-commit install` and must be safe to run more than once (research.md §10).
- [X] T031 [US3] Add a `secrets` job to `.github/workflows/ci.yml` (depends on T025). The job downloads a pinned gitleaks release binary, verifies its checksum, and runs `gitleaks detect --source . --redact --exit-code 1` with `fetch-depth: 0` so history is scanned (FR-010, CI part).
- [X] T032 [US3] Write `README.md` at the repository root with these sections, in order:
  - **Prerequisites**: the verified minimum versions from T020, and the Docker Desktop note (Windows contributors use WSL2 with a Linux distribution, Clarification Session 2026-10-28)
  - **Quickstart**: clone, `cp .env.example .env`, replace placeholder passwords, `make up`, `make test`. Each step must match quickstart.md.
  - **Commands**: a table for `make up`, `make down`, `make reset`, `make lint`, `make test` with one line each
  - **Configuration**: the variable table from data-model.md, and the note that `APP_DB_*` and `POSTGRES_*` changes take effect only after `make reset`, because init scripts run once per volume
  - **Contributor workflow** (FR-012): setup, running checks, creating a branch, opening a change, and the commit-time secret check
  - The README must not include a licence choice (the owner decides; see plan.md research §11).
- [X] T033 [US3] Verify the commit-time block: stage a file containing a fake key in the form `AKIA` followed by 16 uppercase letters, attempt a commit, and confirm the gitleaks hook blocks it and names the file. Then unstage and delete the file (SC-006, quickstart Scenario 5). Requires T001 and T029.

**Checkpoint**: Secrets are protected locally and in CI, and the README is complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Close out the feature's Definition of Done from the constitution.

- [X] T035 Remove the scratch Sync Impact Report comment at the top of `.specify/memory/constitution.md` before the first commit
- [ ] T036 Run quickstart Scenarios 1 to 6 from a clean clone in an empty directory. Record the OS, prerequisite versions, and the timing for Scenario 1 (under 15 minutes, SC-001) and Scenario 2 (under 2 minutes, SC-003) in the PR description
- [ ] T037 Open the pull request against the public repository and confirm that the `secrets` and `checks` jobs both pass on the skeleton (SC-004, FR-007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. T001 needs user approval before it runs.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all stories.
- **User Story 1 (Phase 3, P1)**: Depends on Foundational. This is the MVP.
- **User Story 2 (Phase 4, P2)**: Depends on Foundational and on US1's `up` and `down` targets (T016, T017). Its `test` target needs the stack for the stack tests.
- **User Story 3 (Phase 5, P3)**: T027 and T029 can start after Foundational. T030 and T031 depend on US1 and US2 (`up` target and `ci.yml`). T033 needs T001.
- **Polish (Phase 6)**: Depends on all stories being complete.

### Story Dependencies

- **US1**: Independent after Foundational.
- **US2**: Needs US1's start and stop targets.
- **US3**: Mostly independent. It extends the `up` target and the CI workflow.

### Within Each Story

- Failing tests (T011–T013, T021, T027–T028) come before the implementation they check.
- Test files are created first; implementation files come after.
- Makefile targets are added one per task. They all edit the same file, so they are not marked `[P]`.

### Parallel Opportunities

- Setup: T005 and T006 run alongside T002 and T003.
- Foundational: T007 runs alongside T008.
- US1: T014 and T015 run in parallel (different files).
- US2: T022 runs alongside T021.
- US3: T029 runs alongside T027.

---

## Parallel Example: User Story 1

```bash
# After the failing tests from T011–T013 are written and seen to fail:
Task: "Create docker-compose.yml with the single db service (T014)"
Task: "Create db/init/01-init.sh for the app role and vector extension (T015)"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2 (T001–T010). T001 waits for approval.
2. Complete Phase 3 (T011–T020).
3. Stop and validate: `make up` from a clean clone, the stack is healthy, and the stop and reset commands behave as specified.

### Incremental Delivery

1. Foundation plus US1: the stack starts with one command (MVP).
2. Add US2: one command runs lint and tests locally and in CI.
3. Add US3: environment hygiene, secret blocking, and the README.
4. Polish: quickstart verification and a green CI run on the public repository.

---

## Task Summary

| Scope | Tasks | Count |
|-------|-------|-------|
| Setup | T001–T006 | 6 |
| Foundational | T007–T010, T034 (gate before T014) | 5 |
| User Story 1 (P1, MVP) | T011–T020 | 10 |
| User Story 2 (P2) | T021–T026 | 6 |
| User Story 3 (P3) | T027–T033 | 7 |
| Polish | T035–T037 | 3 |
| **Total** | | **37** |

**Parallel tasks** (marked `[P]`): T005, T006, T007, T014, T015, T022, T029 (7 tasks)

**Independent test criteria**:
- US1: `make up` from a clean clone reports healthy; the vector extension is present; the app role is not a superuser; `make down` keeps data.
- US2: `make test` passes on the skeleton; a deliberate lint violation fails with file and line.
- US3: `.env` is ignored; `.env.example` is complete; a staged fake secret is blocked locally.

**Suggested MVP scope**: User Story 1 (T001–T020). T001 needs user approval before it can run.

---

## Format Validation

All 37 tasks use the checklist format `- [ ] Txxx [P?] [USn?] Description`. Setup, Foundational, and Polish tasks have no story label. Story tasks carry US1, US2, or US3.

## Notes

- Git is not initialised yet, and the public remote is not created. T001 and T037 depend on the user's approval and their remote URL.
- Commit after each task or logical group, once Git is initialised.
- Stop at any checkpoint to validate the story independently.
