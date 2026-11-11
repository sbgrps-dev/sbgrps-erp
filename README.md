# SBGRPS ERP

Internal ERP for Shree Balaji Groups (SBGRPS). Initial implementation covers Shree Balaji Enterprises (SBE) — railway cleaning contracts across ~13 live sites.

**Status:** v0.x pre-release. v1.0 = handover.

## Build order (confirmed 2026-11-09)

1. Stocks / procurement module
2. MS PFTR attendance engine
3. PF / ESI reconciliation

Billing + statutory doc generation are later phases.

## Docs

### Foundation
- [PRD](docs/PRD.md) — product requirements, MVP scope
- [Personas & roles](docs/PERSONAS.md)
- [Use cases](docs/USE-CASES.md)
- [UML](docs/UML.md) — use-case / class / sequence / state diagrams
- [Data model](docs/DATA-MODEL.md) — Postgres schema
- [Tech stack](docs/TECH-STACK.md) — Next.js + FastAPI + Postgres + Coolify
- [Source master draft v1](docs/source-master-draft-v1.md) — prem's original BRD

### Stocks module (phase 1)
- [PRD](docs/stocks/PRD-STOCKS.md)
- [UML](docs/stocks/UML-STOCKS.md)
- [Tech spec](docs/stocks/TECH-SPEC-STOCKS.md) — DB, API, Excel engine, slices S1–S3

### MS PFTR attendance (phase 2)
- [Attendance engine](docs/MSPFTR-ATTENDANCE-ENGINE.md)
- [File spec](docs/MSPFTR-FILE-SPEC.md) — railway input / master / SBE output columns

## Tech stack (summary)

- **Frontend:** Next.js 14 (App Router) · React · TypeScript · shadcn/ui
- **API:** FastAPI (Python 3.12) · Pydantic v2 · SQLAlchemy 2 async · Alembic
- **DB:** PostgreSQL 16
- **Excel:** openpyxl (template-fill, preserves formatting)
- **Hosting:** Docker Compose on Coolify (dev on OptiPlex 3050 Arch); prod on SB Group's server later

## Code

```
apps/api   FastAPI service (uv)        apps/web   Next.js app (pnpm)
infra/     docker-compose.yml          .github/   CI
```

### Run with Docker

```bash
cp .env.example .env          # set POSTGRES_PASSWORD and API_TOKEN
docker compose -f infra/docker-compose.yml --env-file .env up --build -d
docker compose -f infra/docker-compose.yml exec api python -m app.seed   # sites, vendors, Nov-26 products
# open http://localhost:3000
```

### Run for development

```bash
# API (needs a local Postgres 16)
cd apps/api && uv sync
export DATABASE_URL=postgresql+asyncpg://sbgrps:sbgrps@localhost:5432/sbgrps
uv run alembic upgrade head && uv run python -m app.seed
uv run uvicorn app.main:app --reload          # http://localhost:8000/docs

# Web
cd apps/web && pnpm install && pnpm dev        # http://localhost:3000 (proxies /api/v1 to API_URL)

# Tests (API tests need an empty throwaway database)
cd apps/api && TEST_DATABASE_URL=postgresql+asyncpg://sbgrps:sbgrps@localhost:5432/sbgrps_test uv run pytest
```
