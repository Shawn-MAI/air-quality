# Research: Project Foundation and Developer Environment

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

All technical unknowns from the plan's Technical Context are resolved below. No NEEDS CLARIFICATION markers remain.

## 1. Local stack runtime

**Decision**: Docker Compose v2, with a single service defined in `docker-compose.yml`.

**Rationale**: FR-001 and FR-002 require one start command and exactly one service. Compose is the simplest declarative way to define that service, and `docker compose up --wait` blocks until the health check passes, which satisfies FR-006 and SC-002. Compose is free for individual developers and CI runners.

**Alternatives considered**:
- Native Postgres installed through Homebrew or apt: fails Principle V (manual setup outside the README) and FR-001 across macOS and Linux.
- Testcontainers started from pytest: ties the stack lifecycle to tests, so there is no developer-facing start/stop/reset command (FR-003).
- Podman: compatible with Compose files, but Docker is the more common default and the GitHub Actions runners ship with it.

**Constitution impact**: Docker is not in the constitution's default stack list. ADR-0001 records the deviation (Principle VI).

## 2. Database image

**Decision**: `pgvector/pgvector:pg17` (PostgreSQL 17 with the pgvector extension preinstalled), pinned to a specific tag in `docker-compose.yml`.

**Rationale**: The constitution requires pgvector for retrieval (Technical Standards). The official pgvector image ships the extension, so no build step is needed. Pinning the tag keeps local and CI environments identical (Principle V).

**Alternatives considered**:
- Official `postgres:17` plus a custom Dockerfile to install pgvector: adds a build step and a Dockerfile to maintain for no gain.
- PostgreSQL 16: also supported by pgvector, but 17 is the current stable line at the time of planning.
- `latest` tag: rejected because it breaks reproducibility.

## 3. Python version and dependency management

**Decision**: Python 3.12 pinned in `.python-version`, with uv for environment creation, locking (`uv.lock`) and running tools (`uv run`, `uv sync --frozen`).

**Rationale**: Technical Standards require Python 3.12 or newer. uv is a single fast tool that manages the interpreter, environment and lockfile, so no separate pip, venv or pyenv steps are needed (Principle V). `--frozen` keeps CI from silently changing dependencies.

**Alternatives considered**:
- pip with `requirements.txt`: no lockfile by default and more manual steps.
- Poetry: heavier and slower for a skeleton with no packages to publish.

**Minimum prerequisite versions (to verify during implementation)**: Docker Engine with Compose v2 (the `docker compose` subcommand and `--wait` flag), and uv. The implementation will set the exact minimums in the preflight script and README, and the README quickstart will record the versions it was verified with (SC-001).

## 4. Lint and format

**Decision**:
- Python: `ruff check` and `ruff format --check`.
- SQL: `sqlfluff lint` with the `postgres` dialect.
- Secret scan: `gitleaks`, run as a pre-commit hook (`gitleaks protect --staged`) and in CI.

**Rationale**: Technical Standards name ruff and a SQL linter. sqlfluff is the common free SQL linter with a Postgres dialect. gitleaks is free and runs offline, which satisfies FR-010 without a hosted service and Principle XII.

**Alternatives considered**:
- `detect-secrets`: viable, but gitleaks has a broader default rule set and a single binary for CI.
- GitHub's secret scanning: only available to public repos for push protection, and it does not run at commit time locally (FR-010 requires local blocking).
- The `gitleaks-action` GitHub Action: its licence terms differ for organisation-owned repos. The implementation will install a pinned gitleaks binary in CI instead, which keeps it free regardless of owner type.

## 5. Test framework

**Decision**: pytest. Stack-dependent tests connect with `psycopg` (v3) and fail with a message naming `make up` when the stack is not reachable.

**Rationale**: Technical Standards name pytest. FR-005 requires a clear failure that identifies the cause. Failing (not skipping) stack tests prevents a silent green run when the stack is down.

**Alternatives considered**:
- Skip stack tests when the stack is down: hides broken environments and can produce a false pass in CI.
- psycopg2: older API; psycopg v3 is the current maintained driver.

## 6. Command entry point

**Decision**: A `Makefile` with these targets: `up`, `down`, `reset`, `lint`, `test`. `make test` runs `lint` and then pytest, so one command covers FR-004.

**Rationale**: The Done-when criteria require `make up` and `make test`. Make is available on macOS and Linux natively and through WSL2 (Clarification, Session 2026-10-28), so no extra tool is needed. `reset` is a separate target from `down` so that stopping never deletes data (FR-003).

**Alternatives considered**:
- `just`: an extra install for contributors. Rejected to keep prerequisites minimal.
- Shell script: works, but Make gives the target names that the README and CI share.

## 7. Configuration and secrets

**Decision**: `.env.example` lists every variable with purpose and a safe placeholder (FR-008). `.env` is git-ignored (FR-009). `make up` and `make test` run a preflight script that checks Docker, Compose, uv, that the configured port is free, and that required variables are set. Each failure names the problem (FR-013).

**Local credentials (Principle XII)**: The container's bootstrap superuser is used only for initialisation. A separate non-superuser application role is created by an init script (`db/init/01-init.sh`) from `APP_DB_USER` and `APP_DB_PASSWORD`. The Python tests connect as the application role. The init script enables the `vector` extension.

**Port**: The host port is set by `POSTGRES_PORT` (default `5432`) so contributors can change it without editing Compose. The preflight checks the port is free before starting (CHK024).

**Alternatives considered**:
- Single superuser for everything: simpler but fails Principle XII.
- Docker secrets: adds complexity with no benefit for a local-only dev password.

## 8. Reset and data removal

**Decision**: `make down` runs `docker compose down` with no volume flag. `make reset` prints a warning and requires the developer to type `reset` before running `docker compose down --volumes`.

**Rationale**: Clarification Q4 (Session 2026-10-28) chose this split. Confirmation prevents accidental loss.

**Alternatives considered**: a `--force` flag: rejected because it adds a second path that can delete data without the prompt.

## 9. Continuous integration

**Decision**: One GitHub Actions workflow, `.github/workflows/ci.yml`, triggered on pull requests and pushes to `main`. Jobs:
1. `secrets`: runs the pinned gitleaks binary over the repository (FR-010, CI part).
2. `checks`: sets up uv and Docker, copies `.env.example` to `.env`, runs `make up`, runs `make test`, and always runs `make down` at the end.

**Rationale**: FR-006 requires lint, tests and a stack health check on every proposed change. Public repositories get GitHub-hosted runners free of charge (FR-014). Running `make test` in CI exercises the same entry point contributors use, which keeps CI and local checks identical.

**Alternatives considered**:
- Separate lint and test jobs: more visible in the UI, but each job pays setup time. The skeleton is small enough that one job is simpler; this can split later without a constitution change.

## 10. Pre-commit

**Decision**: `.pre-commit-config.yaml` runs ruff (check and format), sqlfluff and gitleaks. `make up` runs `uv run pre-commit install` idempotently so hooks are active after the first start.

**Rationale**: SC-006 requires lint violations and committed secrets to be caught before they reach the shared repository. Installing hooks from `make up` keeps the setup to one documented command (Principle V).

**Alternatives considered**: a separate `make hooks` target: rejected because a contributor could skip it and lose the local protection without noticing.

## 11. Public repository

**Decision**: The repository is configured for public hosting (FR-014). The README and `LICENSE` are added during implementation. The licence choice is a separate decision for the repository owner; it is not part of this plan. The implementation will ask before choosing one.

**Rationale**: FR-014 requires no private infrastructure. Free GitHub Actions minutes for public repositories support Principle VI.
