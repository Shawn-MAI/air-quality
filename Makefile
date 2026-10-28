.PHONY: preflight up down reset lint test

preflight:
	sh scripts/preflight.sh

# sqlfluff is skipped while no .sql files exist: it errors on an empty path set.
lint:
	uv run ruff check .
	uv run ruff format --check .
	@if find db -name '*.sql' | grep -q .; then uv run sqlfluff lint db/; else echo "No SQL files yet; skipping sqlfluff."; fi

test: preflight lint
	uv run --env-file .env pytest

up: preflight
	uv sync --frozen
	docker compose up --wait
	uv run pre-commit install
	@echo "Stack is up. Postgres on 127.0.0.1:$$(grep -E '^POSTGRES_PORT=' .env | cut -d= -f2-)"

down:
	docker compose down

reset:
	@printf 'This deletes the local database volume. Type "reset" to continue: '; \
	read answer; \
	if [ "$$answer" != "reset" ]; then echo "Aborted."; exit 1; fi
	docker compose down -v
