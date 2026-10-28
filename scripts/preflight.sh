#!/bin/sh
# Preflight checks for the local stack (FR-013). Exits 1 and lists every problem found.
# ENV_FILE overrides the environment file; tests use it. The default is .env at the repository root.

DOCKER_COMPOSE_MIN="2.1.1"
UV_MIN="0.4.30"

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd) || exit 1
cd "$REPO_ROOT" || exit 1
ENV_FILE="${ENV_FILE:-.env}"
problems=0

fail() {
  printf '%s\n' "$1"
  problems=$((problems + 1))
}

version_ok() {
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n 1)" = "$1" ]
}

read_var() {
  grep -E "^$1=" "$ENV_FILE" | tail -n 1 | cut -d= -f2-
}

if ! command -v docker >/dev/null 2>&1; then
  fail "docker is not installed. Install Docker Desktop (macOS) or Docker Engine (Linux or WSL2)."
elif ! docker info >/dev/null 2>&1; then
  fail "docker is installed but not running. Start Docker and try again."
fi

compose_version=$(docker compose version --short 2>/dev/null | sed 's/^v//')
if [ -z "$compose_version" ]; then
  fail "Docker Compose v2 is not available. Install the Compose plugin."
elif ! version_ok "$DOCKER_COMPOSE_MIN" "$compose_version"; then
  fail "Docker Compose $DOCKER_COMPOSE_MIN or newer is required; found $compose_version."
fi

if ! command -v uv >/dev/null 2>&1; then
  fail "uv is not installed. See the README for install steps."
else
  uv_version=$(uv --version | awk '{print $2}')
  if ! version_ok "$UV_MIN" "$uv_version"; then
    fail "uv $UV_MIN or newer is required; found $uv_version."
  fi
fi

if [ ! -f "$ENV_FILE" ]; then
  fail "No .env file found. Run: cp .env.example .env"
else
  for var in POSTGRES_PORT POSTGRES_DB POSTGRES_ADMIN_USER POSTGRES_ADMIN_PASSWORD APP_DB_USER APP_DB_PASSWORD; do
    if [ -z "$(read_var "$var")" ]; then
      fail "$var is not set in .env. See .env.example for its purpose."
    fi
  done

  for var in POSTGRES_ADMIN_PASSWORD APP_DB_PASSWORD; do
    case "$(read_var "$var")" in
      change-me-*) fail "$var still has its placeholder value in .env. Replace it with a real secret." ;;
    esac
  done

  port=$(read_var POSTGRES_PORT)
  if [ -n "$port" ] && command -v nc >/dev/null 2>&1; then
    running=$(docker compose ps --status running -q db 2>/dev/null)
    if [ -z "$running" ] && nc -z 127.0.0.1 "$port" >/dev/null 2>&1; then
      fail "POSTGRES_PORT=$port is already in use. Set a free port in .env."
    fi
  fi
fi

if [ "$problems" -gt 0 ]; then
  printf 'Preflight failed with %s problem(s).\n' "$problems"
  exit 1
fi
printf 'Preflight passed.\n'
exit 0
