# ADR-0001: Use Docker Compose for the local development stack

- **Status**: Accepted
- **Date**: 2026-10-28
- **Feature**: [001-dev-env-foundation](../../specs/001-dev-env-foundation/spec.md)

## Context

The constitution requires one documented command to bring up the local stack (Principle V) and requires that no paid dependency be used without an ADR (Principle VI). The stack needs one service in this feature: PostgreSQL 17 with pgvector. Later features will add services, so the approach must extend cleanly.

Docker Compose is not in the constitution's default stack list, so its use is a deviation that this ADR records.

## Decision

Use Docker Compose v2 with a `docker-compose.yml` at the repository root to define all local services. Use the `pgvector/pgvector:pg17` image with a pinned tag.

## Consequences

- Positive: one start command, health checks, and reproducible service definitions for both local use and CI.
- Positive: free for individual developers and for GitHub-hosted runners on public repositories.
- Negative: contributors must install Docker Desktop (macOS) or Docker Engine with Compose v2 (Linux or WSL2). This is a prerequisite that the README and preflight script must state.
- **Licence check (verified 2026-10-28)**: Docker's pricing page lists Docker Desktop, Docker Engine and Docker Hub under the free Docker Personal plan ($0, 1 user, 100 anonymous Docker Hub pulls per hour, "reasonable use" for logged-in users). That covers this personal, non-commercial project. The pricing page is not the licence text, so re-check the Docker Desktop licence agreement if the project is ever used commercially. If the terms stop allowing the intended use, switch to Docker Engine on Linux and WSL2, or to a free alternative, and supersede this ADR.

## Alternatives considered

- **Native PostgreSQL installed by hand**: rejected, because it breaks Principle V.
- **Testcontainers from pytest**: rejected, because there is no developer-facing start, stop and reset command.
- **Podman with Compose files**: compatible, but less common on the platforms this project targets.
