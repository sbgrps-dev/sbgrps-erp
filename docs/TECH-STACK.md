# SBGRPS ERP — Tech stack (v0.1)

**Version:** v0.1 · 2026-11-10 · Agreed with prem.

## 1. Overview

| Layer | Choice | Version |
|---|---|---|
| Frontend | Next.js (App Router) + React + TypeScript | Next.js 14 · Node 20 LTS |
| UI kit | shadcn/ui as the base; compose with 21st.dev, Magic UI, React Bits | shadcn CLI latest |
| Frontend data | TanStack Query · Zod · React Hook Form | latest stable |
| API | FastAPI (Python) + Pydantic v2 | Python 3.12 · FastAPI 0.115+ |
| ORM & migrations | SQLAlchemy 2.x (async) + Alembic | 2.0+ |
| Database | PostgreSQL | 16 |
| Excel engine | openpyxl (fill the template, preserve merges/formulas/borders). Pandas only for data analysis, never for writing the output. | 3.1+ |
| Auth | NextAuth on the front; FastAPI dep validating JWT | later adds Google Workspace SSO |
| Email (last in the build order) | Gmail API from `deivanayagam.k@sbgrps.com` for ingestion; `sbgrps.dev@gmail.com` for outgoing drafts | via `google-api-python-client` |
| Background jobs | FastAPI BackgroundTasks for now; Celery + Redis when email ingestion + attendance arrive | — |
| Packaging | Docker + Docker Compose. One `docker-compose.yml` for dev; same images deployed in prod | Docker 24+ |

## 2. Why these

- **Next.js + shadcn**: production-quality UI without rebuilding primitives. Owning the components (shadcn copies code into your repo) means no library lock-in.
- **FastAPI**: async, type-safe via Pydantic, free OpenAPI spec that generates a matching TypeScript client. Enough throughput for an internal ERP by a factor of hundreds.
- **openpyxl over pandas**: the September Excel template has merged cells, styled headers, column widths and formulas. openpyxl keeps all of that when you open + edit + save. Pandas strips formatting.
- **Postgres 16**: row-level security policies enforce per-site access without us re-checking in every query. Full-text search indexes power the product search.
- **Docker Compose**: one definition runs dev on the home box and prod on SB Group's server. No per-env drift.

## 3. Repo layout (planned)

```
sbe-erp/
├── apps/
│   ├── web/              Next.js app
│   └── api/              FastAPI app
├── packages/
│   └── shared-types/     Generated TS types from the OpenAPI spec
├── infra/
│   ├── docker-compose.yml
│   ├── Dockerfile.web
│   ├── Dockerfile.api
│   └── Caddyfile
├── docs/                 everything from /mnt/project-files/erp-docs/ moves here
├── .github/workflows/    CI (lint, type-check, test, build)
├── README.md
└── LICENSE
```

Monorepo with pnpm workspaces for the frontend side, uv or Poetry for the Python side.

## 4. Environments

| Environment | Where | Purpose | Data |
|---|---|---|---|
| Dev (local) | OptiPlex 3050, Arch, Docker | prem and co-builder developing | anonymised seed data |
| Staging | same 3050, parallel Coolify project | demos, migrations before prod | copy of prod minus PII |
| Production | SB Group's own server (budgeted ₹10L+) | SBGRPS staff daily use | real data, daily off-site backups |

The OptiPlex 3020 is unused — not a firewall, not a dependency.

## 5. Hosting panel on the 3050 — Coolify

[Coolify](https://coolify.io) runs a self-hosted PaaS dashboard on the OptiPlex 3050. It gives us deploy-from-Git, managed Postgres, automatic Let's Encrypt, per-service logs, metrics and env vars, and daily DB backups to local disk.

Install when ready:
```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```
Then open `http://<3050-ip>:8000`, create an admin user, connect GitHub.

Each service (web, api, db) becomes a Coolify resource pointing at the same Git repo. Push to `main` → auto-rebuild + redeploy.

## 6. Production goes to SB Group's server later

- Same `docker-compose.yml` as dev + staging; zero code changes, just env vars.
- SB Group's IT runs the box; we hand over the compose file, the Alembic migration runner and the backup script.
- Cloudflare (free tier) in front for HTTPS, DDoS and a stable DNS name even when the server IP changes.

## 7. CI (GitHub Actions)

- `lint`: ruff + eslint + prettier
- `type-check`: mypy + tsc
- `test`: pytest + vitest
- `build`: both Docker images
- `deploy-staging`: on merge to `main`, Coolify webhook triggers staging rebuild

## 8. Security basics (from day 1)

- Secrets in Coolify env vars, never committed. `.env.example` tracked.
- Postgres: `aadhaar_encrypted`, `bank_account_encrypted` columns using pgcrypto / `encrypt_iv`. Decryption only via a dedicated helper that writes an `audit_log` row.
- Backups are encrypted (age or restic with a passphrase).
- No service exposed to the internet without TLS.

## 9. Versioning and branching

- Semver inside v0.x while pre-release. v1.0 = handover.
- Trunk-based: branch per change, PR with review from the co-builder, squash merge.
- Each PR body uses the project's attribution footer (already configured for this thread).

## 10. What's *not* in the stack

- Pterodactyl (game-server panel, irrelevant).
- Any custom firewall PC — not a real security layer.
- GraphQL, gRPC, Kafka — unnecessary for an internal ERP.
- Nginx hand-config — Caddy inside Coolify handles everything.
- A separate home-brewed hosting panel — Coolify already is one.
