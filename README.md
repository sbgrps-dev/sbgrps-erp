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

### MS PFTR attendance (phase 2)
- [Attendance engine](docs/MSPFTR-ATTENDANCE-ENGINE.md)
- [File spec](docs/MSPFTR-FILE-SPEC.md) — railway input / master / SBE output columns

## Tech stack (summary)

- **Frontend:** Next.js 14 (App Router) · React · TypeScript · shadcn/ui
- **API:** FastAPI (Python 3.12) · Pydantic v2 · SQLAlchemy 2 async · Alembic
- **DB:** PostgreSQL 16
- **Excel:** openpyxl (template-fill, preserves formatting)
- **Hosting:** Docker Compose on Coolify (dev on OptiPlex 3050 Arch); prod on SB Group's server later
