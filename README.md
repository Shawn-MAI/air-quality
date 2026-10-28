# Air-Quality Intelligence Platform

A personal data engineering and applied AI project that runs entirely on free tiers. This repository currently holds the developer environment foundation: a local Postgres with pgvector, lint and test tooling, secret checks, and CI.

## Prerequisites

- **macOS or Linux**: Docker Desktop (macOS) or Docker Engine with Compose v2 (Linux).
- **Windows**: use WSL2 with a Linux distribution, and run every command inside that distribution.
- Docker Compose v2.1.1 or newer, and [uv](https://docs.astral.sh/uv/) 0.4.30 or newer. `make up` checks both and stops with a clear message if they are missing.
- `make`, `git`, and `openssl`.

Docker Desktop is free for personal use. See [ADR-0001](docs/adr/0001-local-stack-docker-compose.md) for the licence check.

## Quickstart

```sh
git clone https://github.com/Shawn-MAI/air-quality.git
cd air-quality
cp .env.example .env
# Replace both change-me-* placeholders in .env with real values.
make up
make test
```

`make up` checks prerequisites, installs Python dependencies, starts the database, waits until it is healthy, and installs the pre-commit hooks. It is safe to run again.

If you have not replaced the placeholder passwords, `make up` stops and names the variable that still needs a value.

## Commands

| Command | What it does |
|---------|--------------|
| `make up` | Checks prerequisites, starts the local stack, waits until healthy, installs hooks |
| `make down` | Stops the stack and keeps the data |
| `make reset` | Stops the stack and deletes the database volume after you type `reset` |
| `make lint` | Runs ruff and sqlfluff |
| `make test` | Runs preflight, lint, and the pytest suite |

## Configuration

Settings live in `.env`, which is git-ignored. `.env.example` lists every variable with a comment.

| Variable | Purpose |
|----------|---------|
| `POSTGRES_PORT` | Host port for the database, bound to 127.0.0.1 |
| `POSTGRES_DB` | Database name |
| `POSTGRES_ADMIN_USER` | Local admin role created by the database image |
| `POSTGRES_ADMIN_PASSWORD` | Password for the admin role (must be replaced) |
| `APP_DB_USER` | Non-superuser application role created on first start |
| `APP_DB_PASSWORD` | Password for the application role (must be replaced) |

Database roles and the database name are set when the data volume is first created. Changing these values in `.env` takes effect only after `make reset`.

## Contributor workflow

1. Create a branch from `main`, for example `git switch -c 002-my-feature`.
2. Make your change, then run `make test`. It must pass before you open a pull request.
3. Commit. The pre-commit hooks run ruff, sqlfluff, and gitleaks on staged files. A commit that contains a secret is blocked, and the hook names the file.
4. Push the branch and open a pull request. CI runs the `checks` job (stack, lint, tests) and the `secrets` job (gitleaks over the full history).

Features follow the spec-driven workflow in [`.specify/memory/constitution.md`](.specify/memory/constitution.md): specification, plan, tasks, then implementation, each on its own branch.

Never commit `.env` or any real credential. Only `.env.example` belongs in version control.

## Troubleshooting

- **"Docker is installed but not running"**: start Docker Desktop (or the Docker service on Linux), then run `make up` again.
- **"Stack is not running"** from a test: run `make up` first.
- **Changed a password in `.env` but login fails**: run `make reset`, then `make up`.
