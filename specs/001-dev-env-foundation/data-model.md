# Data Model: Project Foundation and Developer Environment

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

This feature stores no business data. The data store it starts is empty apart from the `vector` extension and the application role. The entities below are the configuration concepts from the spec's Key Entities section. They are not database tables.

## Local Stack

| Attribute | Type | Rules |
|-----------|------|-------|
| `service_name` | string | Exactly one value in this feature: `db` |
| `image` | string | Pinned tag (`pgvector/pgvector:pg17`), never `latest` |
| `health_status` | enum | `starting`, `healthy`, `unhealthy`, `stopped` (from the Compose health check) |
| `host_port` | integer | From `POSTGRES_PORT`, default `5432`, must be free before start |

**State transitions**: `stopped` → `starting` → `healthy`. A failed health check moves to `unhealthy`. `make down` moves any state to `stopped` and keeps the data volume.

## Environment Configuration

| Variable | Secret | Default in `.env.example` | Purpose |
|----------|--------|---------------------------|---------|
| `POSTGRES_PORT` | no | `5432` | Host port for the data store |
| `POSTGRES_DB` | no | `airquality` | Database name |
| `POSTGRES_ADMIN_USER` | no | `airquality_admin` | Bootstrap superuser, used only by container initialisation |
| `POSTGRES_ADMIN_PASSWORD` | yes | `change-me-admin` | Bootstrap superuser password (placeholder; replace locally) |
| `APP_DB_USER` | no | `airquality_app` | Non-superuser role used by the application and tests |
| `APP_DB_PASSWORD` | yes | `change-me-app` | Application role password (placeholder; replace locally) |

Validation rules, enforced by the preflight script (FR-013):
- Every variable above must be set and non-empty.
- Secret variables must not equal their `.env.example` placeholder when the stack starts. The preflight fails with exit `1` and names the variable. The README tells contributors to replace each placeholder before `make up`. CI generates real values before it starts the stack (T025).
- `.env` is git-ignored (FR-009). The secret scan blocks commits that contain likely secrets (FR-010).
