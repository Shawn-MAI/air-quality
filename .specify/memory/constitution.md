<!--
SYNC IMPACT REPORT (scratch for human review; remove before committing)
Version change: none (new document, template placeholders resolved) -> 1.0.0
Modified principles: none (initial adoption)
Added sections: Core Principles I-XII; Technical Standards; Development Workflow and Quality Gates; Governance
Removed sections: none (template's five-principle and placeholder sections replaced by the requested structure)
Deferred TODOs: none
-->
# Air-Quality Intelligence Platform Constitution

This constitution governs a personal data engineering and applied AI project that MUST run on free tiers only.

## Core Principles

### I. Specification First
- Implementation MUST NOT start until a spec, plan, and task list for the feature are approved.
- Every plan MUST pass a Constitution Check against these principles.
- Any violation MUST be justified in the plan's complexity table.

**Rationale**: Written intent prevents rework and keeps scope honest on a solo project where drift is easy.

### II. Idempotent, Replayable Pipelines
- Every pipeline MUST be safe to re-run and to backfill for any date range.
- Re-runs MUST NOT create duplicates or other side effects.
- Writes SHOULD be keyed and merged rather than blindly appended.

**Rationale**: Scheduled retries, API failures, and backfills make re-runs routine, so they must be harmless.

### III. Immutable Raw Data, Versioned Transformations
- Bronze (raw) data MUST be stored exactly as received, together with run metadata.
- Bronze data MUST NOT be edited in place. Corrections come from re-ingestion or downstream logic.
- All transformations MUST be code kept in version control.

**Rationale**: Untouched raw history allows reprocessing with new logic and auditing of every published value.

### IV. Contracts and Tests Before Data Products
- Each published dataset MUST have a data contract covering schema, owner, freshness target, and null-rate limits.
- Tests MUST be written first and MUST fail first before the behaviour they check is implemented.
- Test failures MUST block publication of the affected dataset.

**Rationale**: Contracts make quality explicit, and test-first confirms the tests can actually detect failures.

### V. Reproducible From a Clean Checkout
- One documented command MUST bring up the complete local stack.
- Infrastructure MUST be defined as code.
- No manual setup steps MAY exist outside the README.

**Rationale**: A personal project is only maintainable if it can be rebuilt from scratch after a long gap.

### VI. Free Tier First, Cost Visible
- No paid dependency MAY be introduced without an ADR.
- Every external API and LLM route MUST have a request cap and usage recording.
- Free-tier terms and licences, including attribution and non-commercial limits, MUST be respected.

**Rationale**: The project must stay at zero cost. Caps and usage records surface accidental overage before it happens.

### VII. Schema-Validated AI Outputs
- LLM output MUST be validated against a typed schema before it enters any table.
- Output that fails validation or is low-confidence MUST go to a quarantine table with a recorded reason.
- Quarantined output MUST NOT enter trusted data.

**Rationale**: Models produce plausible but malformed output. Isolating it keeps published data trustworthy.

### VIII. Least-Privilege Agents
- Agents MUST receive read-only tools by default.
- Any write action MUST require explicit human approval.
- Every tool call MUST be logged.
- Every agent answer MUST cite the data or documents it used.

**Rationale**: This limits the impact of model error and makes every answer auditable.

### IX. Evals Gate AI Changes
- Any change to a prompt, model, retrieval configuration, or agent tool MUST pass the evaluation suite in CI before merge.

**Rationale**: AI behaviour can regress silently. The evaluation suite is the only reliable regression signal.

### X. Observability and Traceability
- Pipelines MUST emit structured logs, lineage, and freshness metrics.
- Every LLM call MUST be traced with latency, token usage, and cost.

**Rationale**: Freshness and spend should be answerable from data, not guesswork.

### XI. Simplicity and Thin Vertical Slices
- The simplest design that meets the spec MUST be preferred.
- Speculative abstractions MUST NOT be added.
- Extra services SHOULD NOT be added without demonstrated need.
- Each feature MUST deliver something demonstrable end to end.

**Rationale**: Maintenance time is the scarce resource on a solo project, and thin slices produce working results early.

### XII. Security and Privacy
- Secrets MUST NOT be committed to the repository. They MUST be supplied through the environment or a secret store.
- Personal data MUST NOT be sent to hosted LLMs.
- Every service MUST use least-privilege credentials.

**Rationale**: Hosted services are third parties and leaked credentials or personal data are costly and hard to undo.

## Technical Standards

- **Languages**: Python 3.12 or newer with type hints MUST be used. SQL MUST be used for models.
- **Linting and testing**: Python MUST be linted with ruff and tested with pytest. SQL style MUST be enforced by a SQL linter.
- **Layers and naming**: Tables MUST use the `bronze_`, `silver_`, and `gold_` prefixes. All timestamps MUST be stored in UTC. Units MUST be normalised in silver.
- **Default stack**: dlt for ingestion, Delta Lake tables, DuckDB for local queries, dbt Core for transformation, Apache Airflow for orchestration, pgvector for retrieval, LiteLLM as the only gateway to models, Ollama for local models, Langfuse for tracing and evals, FastAPI for APIs, and GitHub Actions for CI. Any deviation MUST be recorded in an ADR.
- **Versioned contracts**: Every dataset, API, and agent tool MUST have a versioned contract. Breaking changes MUST create a new version.

## Development Workflow and Quality Gates

- **Order**: Each feature MUST proceed in this order: specify, clarify, plan, tasks, analyze, implement. Each feature MUST be developed on its own branch.
- **Definition of done**: A feature is done only when all of the following hold:
  - tests and data tests pass in CI;
  - the data contract is updated;
  - docs and ADRs are updated;
  - the quickstart works from a clean checkout;
  - the spec's success criteria are demonstrated.
- **Dependencies**: A feature MUST NOT start until all features it depends on are merged.

## Governance

- This constitution supersedes other project practices.
- Amendments MUST be made through the constitution command. Each amendment MUST include a written reason and a semantic version bump.
- **Versioning policy**:
  - MAJOR: backward-incompatible removal or redefinition of a principle or governance rule.
  - MINOR: a new principle or section, or materially expanded guidance.
  - PATCH: clarifications, wording, typo fixes, and non-semantic refinements.
- **Compliance**: Every plan and every review MUST check compliance with this constitution. Unjustified violations MUST block approval.

**Version**: 1.0.0 | **Ratified**: 2026-10-27 | **Last Amended**: 2026-10-28
