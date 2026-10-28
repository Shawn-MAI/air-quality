# Developer Interface Contract: Project Foundation and Developer Environment

**Version**: 1.0.0 | **Feature**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

This contract defines the commands contributors and CI use. Under the constitution, a breaking change to a command requires a new major version of this contract.

## Commands

All commands run from the repository root through `make`.

### `make up`

Starts the local stack.

- **Steps**: preflight checks → install git hooks (idempotent) → `uv sync --frozen` → `docker compose up --wait`.
- **Preconditions**: Docker with Compose v2, uv, `.env` present with all required variables set, configured port free.
- **Success**: exit code `0`; the `db` service reports `healthy`; the application role can connect.
- **Failure**: exit code `1`, with one line per problem naming it (for example `POSTGRES_PORT 5432 is in use` or `APP_DB_USER is not set in .env`) (FR-013).
- **Idempotent**: running it twice leaves the stack running and does not recreate the data volume.

### `make down`

Stops the local stack and removes its containers. Keeps data.

- **Success**: exit code `0`; no containers from this project are running; the data volume still exists.
- **Data**: never deletes data (FR-003).

### `make reset`

Deletes all stored data for the local stack.

- **Prompt**: prints a warning and waits for the developer to type `reset`. Any other input cancels with exit code `1` and no changes.
- **Success**: exit code `0`; containers and the data volume are removed. The next `make up` starts an empty database.

### `make lint`

Runs `ruff check`, `ruff format --check`, and `sqlfluff lint`.

- **Success**: exit code `0`.
- **Failure**: exit code `1`; each violation prints file, line and rule (FR-005).

### `make test`

Runs `make preflight` and `make lint`, then pytest over the full suite (`uv run --env-file .env pytest`).

- **Preconditions**: `.env` exists with no placeholder secrets (preflight). The stack is running for stack-dependent tests.
- **Success**: exit code `0`; pytest summary shows pass.
- **Failure**: the failing step's exit code is returned through make, which reports `2` for a failed recipe. Each pytest or lint failure names the test or file and line (FR-005). A stack-dependent test that cannot connect fails with a message naming `make up`.
- **Time budget**: under 2 minutes on the empty skeleton (SC-003).

## CI contract

Workflow: `.github/workflows/ci.yml`. Runs on pull requests and on pushes to `main`.

| Job | Steps | Pass condition |
|-----|-------|----------------|
| `secrets` | Pinned gitleaks binary over the repository | No findings |
| `checks` | Copy `.env.example` to `.env` → `make up` → `make test` → `make down` (always) | All steps exit `0` |

## Environment contract

Every variable read by a command is listed in `.env.example` with its purpose and a safe placeholder (FR-008). See [data-model.md](../data-model.md) for the variable table.
