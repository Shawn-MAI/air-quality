# Implementation Plan: Project Foundation and Developer Environment

**Branch**: `001-dev-env-foundation` | **Date**: 2026-10-28 | **Spec**: [spec.md](./spec.md) | **Status**: Approved (2026-10-28)

**Input**: Feature specification from `/specs/001-dev-env-foundation/spec.md`

## Summary

A contributor clones the repository, copies `.env.example` to `.env`, and runs `make up` to start a local stack that contains one service: PostgreSQL 17 with pgvector. `make test` runs lint (ruff, sqlfluff) and pytest. Stack-dependent tests report a clear message when the stack is down. Pre-commit runs ruff and a gitleaks secret check at commit time, and GitHub Actions runs the same checks plus a stack start on every change to a public repository. All tools are free. Technical choices and their alternatives are recorded in [research.md](./research.md).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12 with type hints; SQL (PostgreSQL dialect); POSIX shell for the preflight and database init scripts

**Primary Dependencies**: Docker Compose v2 (local stack); uv (Python and lockfile); ruff, pytest, sqlfluff, pre-commit, gitleaks, psycopg (dev tooling and tests); GNU Make (entry point)

**Storage**: PostgreSQL 17 with pgvector, in a named Docker volume (local development only)

**Testing**: pytest (unit-level config checks and stack-dependent tests); ruff and sqlfluff for lint

**Target Platform**: macOS and Linux natively; Windows through a Linux environment (WSL2) (Clarification, Session 2026-10-28)

**Project Type**: Local developer environment and CI configuration (infrastructure as code; no application runtime yet)

**Performance Goals**: Every stack service healthy within 5 minutes (SC-002); `make test` passes on the empty skeleton within 2 minutes (SC-003)

**Constraints**: Free tier only (Principle VI); no secrets in the repository (Principle XII); one documented start command (Principle V); single data-store service only (FR-002, Clarification Session 2026-10-28)

**Scale/Scope**: One developer machine plus one CI pipeline; one service; no pipelines or business logic in this feature

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status | Notes |
|-----------|------|--------|-------|
| I. Specification first | Spec, clarification and plan approved before tasks and code | PASS | Spec clarified in five answers; this plan precedes tasks |
| II. Idempotent pipelines | Pipelines re-runnable | N/A | No pipelines in this feature |
| III. Immutable raw data | Bronze data stored as received | N/A | No data ingested |
| IV. Contracts and tests first | Tests written and failing before implementation | PASS | tasks.md must order failing tests before the compose, script and workflow changes; the contributor interface is contracted in [contracts/developer-interface.md](./contracts/developer-interface.md) |
| V. Reproducible from clean checkout | One documented start command; infrastructure as code | PASS | `make up` runs preflight, `uv sync --frozen` and `docker compose up --wait`; `docker-compose.yml` is the infrastructure definition |
| VI. Free tier first | No paid dependency without an ADR; licences respected | PASS with action | Docker is the one new tool outside the constitution's default stack; [ADR-0001](../../docs/adr/0001-local-stack-docker-compose.md) must confirm the current Docker Desktop terms before the feature is merged |
| VII. Schema-validated AI output | LLM output validated | N/A | No LLM in this feature |
| VIII. Least-privilege agents | Read-only tools, logged calls | N/A | No agents in this feature |
| IX. Evals gate AI changes | Eval suite in CI | N/A | No AI changes |
| X. Observability | Structured logs, lineage, freshness | N/A | No pipelines to observe; the stack health check is the only signal |
| XI. Simplicity | Simplest design; no extra services | PASS | One service; no speculative abstractions; see Complexity Tracking for the small additions |
| XII. Security and privacy | No secrets in repo; least-privilege credentials | PASS | `.env` is git-ignored; gitleaks runs at commit time and in CI; the application connects as a least-privilege role; no personal data |

**Technical Standards check**: Python 3.12 with type hints (PASS); ruff and pytest (PASS); SQL linted with sqlfluff (PASS, applied to the one SQL file now and to all SQL later); uv for dependency management (PASS); pgvector for retrieval (PASS); GitHub Actions for CI (PASS); Docker Compose is not in the default stack list, so ADR-0001 records the choice (PASS with action).

**Result**: No unjustified violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/001-dev-env-foundation/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.
├── .env.example                  # Every variable, purpose, placeholder (FR-008)
├── .gitignore                    # Excludes .env and credentials (FR-009)
├── .pre-commit-config.yaml       # ruff, sqlfluff, gitleaks at commit time (FR-010)
├── .python-version               # 3.12
├── .sqlfluff                     # postgres dialect
├── Makefile                      # up, down, reset, lint, test (FR-001, FR-003, FR-004)
├── README.md                     # Quickstart and contributor workflow (FR-011, FR-012)
├── docker-compose.yml            # Single db service: pgvector/pgvector:pg17 (FR-002)
├── pyproject.toml                # Python 3.12, ruff, pytest, psycopg (dev group)
├── uv.lock                       # Locked dependencies, used with uv sync --frozen
├── db/
│   └── init/
│       └── 01-init.sh            # Enables vector; creates least-privilege app role
├── scripts/
│   └── preflight.sh              # Checks Docker, uv, port, required variables (FR-013)
├── tests/
│   ├── conftest.py               # Stack connection fixture; clear failure when down
│   └── test_stack.py             # Stack health and role checks
├── docs/
│   └── adr/
│       └── 0001-local-stack-docker-compose.md
└── .github/
    └── workflows/
        └── ci.yml                # secrets and checks jobs (FR-006, FR-010)
```

**Structure Decision**: A single flat repository with infrastructure at the root (`docker-compose.yml`, `Makefile`, `.github/`), Python tooling in `pyproject.toml`, and tests under `tests/`. There is no `src/` package yet because this feature has no application code. The first pipeline feature will add the package layout and record it in its own plan. Directories for bronze, silver and gold layers are added by later features, not here (Principle XI).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Only one item is a deviation from the constitution's default stack, and it is recorded in ADR-0001. The rest are not violations but are listed because they add files:

| Item | Why Needed | Simpler Alternative Rejected Because |
|------|------------|-------------------------------------|
| Docker Compose (not in default stack) | One command must start the stack (Principle V) and the stack must be reproducible | Hand-installed PostgreSQL breaks Principle V; see ADR-0001 |
| `db/init/01-init.sh` creates a second, non-superuser role | Principle XII requires least-privilege credentials for every service | Using the bootstrap superuser for the application and tests breaks Principle XII |
| `scripts/preflight.sh` | FR-013 requires early failures that name the missing prerequisite | Letting Docker or uv fail with their own errors does not name the project's required variables or port |

**Post-design re-check**: After Phase 1, the Constitution Check still passes. The data model and contract add no new services, no paid dependencies, and no AI components. Principle VI remains conditional on the ADR-0001 licence check before merge.
