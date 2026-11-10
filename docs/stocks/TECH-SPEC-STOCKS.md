# SBGRPS ERP — Stocks module tech spec

**Version:** v0.1 · 2026-11-10 · Implements [PRD-STOCKS.md](PRD-STOCKS.md) v0.3 and [UML-STOCKS.md](UML-STOCKS.md) v0.3 on the stack in [../TECH-STACK.md](../TECH-STACK.md).

## 1. Delivery slices

| Slice | What ships | Status |
|---|---|---|
| **S1** | Sites, vendors, products, prices + history, monthly requisitions per site, line maths, review preview, Excel generation (September layout, single-site and consolidated), Save / Reopen, Mark sent manually, per-vendor price sheet download, manual price update, audit log | this PR |
| **S2** | Vendor price reply capture (upload the reply file / paste prices) → Accept / Reject per line → new `ProductPrice` | next |
| **S3** | Email (last phase): Gmail drafts for *Send to HQ* and *Send price list to vendors*, sent-record + message-ID | last |

S1 is useful on its own: prem builds the month, downloads the workbook, sends it from Gmail himself and clicks **Mark sent manually**.

## 2. Repo layout

```
apps/api/                FastAPI service (Python 3.12, uv)
  app/main.py            app factory, routers, CORS, auth dependency
  app/config.py          settings from env (pydantic-settings)
  app/db.py              async engine + session dependency
  app/models/            SQLAlchemy 2.x models (core.py, stocks.py)
  app/schemas/           Pydantic v2 request/response models
  app/routers/           sites, vendors, products, requisitions, months, price_lists
  app/services/          money.py (line maths), requisitions.py, audit.py
  app/excel/             requisition_workbook.py, price_sheet.py, styles.py
  app/seed/              seed data + `python -m app.seed`
  alembic/               migrations
  tests/                 pytest (unit + API against a real Postgres)
apps/web/                Next.js 14 App Router + TS + Tailwind + TanStack Query
  src/app/stocks/...     requisitions, products, vendors, price-lists pages
  src/app/api/[...path]  server-side proxy to the API (attaches API token)
  src/components/ui/     shadcn-style primitives (button, input, card, table, tabs)
infra/docker-compose.yml db + api + web
.github/workflows/ci.yml lint, tests, web build
```

## 3. Database (Postgres 16)

All tables have `id bigint identity PK`, `created_at`, `updated_at` (timestamptz). Money is `numeric(12,2)`, quantities `numeric(12,3)`, GST rate `numeric(5,2)` (percent, e.g. `18.00`).

| Table | Key columns | Constraints / notes |
|---|---|---|
| `site` | `code`, `display_name`, `is_active`, `sort_order` | `code` unique. `MSPFTR_PT` = "MS PFTR & PT"; `MS_OFFICE` separate |
| `vendor` | `name`, `address` (text, multi-line), `gstin`, `emails text[]`, `phones text[]`, `website`, `drug_licence`, `products_supplied` (text), `is_active` | `name` unique (case-insensitive index) |
| `product` | `code`, `name`, `aliases text[]`, `unit`, `hsn`, `gst_rate`, `is_active` | `code` unique; `gst_rate` between 0 and 28; trigram-free search (see §5) |
| `product_vendor` | `product_id`, `vendor_id`, `is_preferred` | unique `(product_id, vendor_id)`; partial unique index: one preferred per product |
| `product_price` | `product_vendor_id`, `price`, `effective_from`, `effective_to` (null = current), `source` (`seed`/`office_edit`/`vendor_reply`), `reason` | partial unique index: one current row per `product_vendor_id`; `price >= 0` |
| `stock_requisition` | `site_id`, `month` (date, 1st of month), `status`, `saved_at`, `sent_at`, `sent_via` (`manual`/`app`), `notes` | unique `(site_id, month)`; `status` check in (`draft`,`saved`,`sent_to_hq`,`sent_manually`,`closed`) |
| `requisition_line` | `requisition_id`, `product_id`, `vendor_id`, `qty_required`, `unit_snapshot`, `price_snapshot`, `gst_rate_snapshot`, `taxable_amount`, `gst_amount`, `line_total`, `notes` | unique `(requisition_id, product_id, vendor_id)`; `qty_required > 0`; FK `on delete cascade` from requisition only |
| `generated_workbook` | `month`, `scope` (`site`/`month`), `requisition_id` (null for month scope), `site_ids bigint[]`, `version`, `filename`, `content bytea`, `grand_total` | unique `(month, scope, requisition_id, version)`; old versions kept (FR-OUT-3) |
| `audit_log` | `entity`, `entity_id`, `action`, `field`, `old_value`, `new_value`, `reason`, `actor`, `at` | append-only |

Workbooks are stored in Postgres (`bytea`): they are ~25 KB, and this keeps backups to one `pg_dump`.

Totals on the requisition are **not stored**; they are summed from lines on read (no drift).

S2 adds `price_list_request`, `price_list_reply`, `price_list_reply_line`. S3 adds `hq_email`, `price_list_email`.

## 4. Line maths (one place: `app/services/money.py`)

```
taxable   = round_half_up(qty × price, 2)
gst       = round_half_up(taxable × gst_rate / 100, 2)
total     = taxable + gst
```

`Decimal` only, never float. Matches the Nov-26 file to the paisa (e.g. 100 × 75.68 = 7568.00, GST 1362.24; 40 × 89.61 = 3584.40, GST 645.19).

When a line is added, unit / price / GST rate are **snapshotted** from the product and the chosen vendor's current price. Later catalogue changes do not touch existing lines.

## 5. Product search

`GET /api/v1/products?q=sterix` — case-insensitive match on `name`, `code` or any alias, after normalising both sides (lower-case, strip spaces, `-`, `.`, `(`, `)`). So `STERIX-A super`, `STERIX A SUPER`, `sterixa` all hit the same product. Implemented in SQL with `regexp_replace(lower(...))` and `unnest(aliases)`; the catalogue is a few hundred rows, so no index is needed yet.

## 6. API (REST, `/api/v1`, JSON)

| Method & path | Purpose |
|---|---|
| `GET /sites` · `POST /sites` · `PATCH /sites/{id}` | Site list / add / rename / deactivate |
| `GET /vendors` · `POST /vendors` · `PATCH /vendors/{id}` | Vendor directory |
| `GET /products?q=&vendor_id=` | Search catalogue (with vendors + current prices) |
| `POST /products` | Create product, incl. inline-add from the requisition (needs ≥1 vendor + price) |
| `PATCH /products/{id}` | Edit name, aliases, unit, HSN, GST |
| `POST /products/{id}/vendors` | Link another approved vendor with its price |
| `POST /products/{id}/vendors/{vendor_id}/prices` | New price (closes the current row, `reason` required) |
| `GET /products/{id}/prices` | Price history |
| `GET /months/{yyyy-mm}/requisitions` | All sites for the month: status, line count, totals (creates nothing) |
| `PUT /months/{yyyy-mm}/sites/{site_id}/requisition` | Get-or-create the Draft for (site, month) |
| `GET /requisitions/{id}` | Requisition with lines and totals |
| `POST /requisitions/{id}/lines` | Add line `{product_id, qty, vendor_id?}` (vendor defaults to preferred) |
| `PATCH /requisitions/{id}/lines/{line_id}` | Change qty / vendor / notes; or `price` + `price_reason` → new `ProductPrice` (source `office_edit`) and re-snapshot |
| `DELETE /requisitions/{id}/lines/{line_id}` | Remove line |
| `GET /requisitions/{id}/preview` | Review pane data: exactly the rows the workbook will contain |
| `POST /requisitions/{id}/workbooks` | Generate single-site workbook → new version |
| `POST /requisitions/{id}/save` · `/reopen` | Draft → Saved · Saved → Draft |
| `GET /months/{yyyy-mm}/preview?site_ids=` | Consolidated review (all sites with lines) |
| `POST /months/{yyyy-mm}/workbooks` `{site_ids?}` | Generate consolidated workbook (the HQ file) |
| `GET /workbooks?month=` · `GET /workbooks/{id}/download` | Version history · download `.xlsx` |
| `POST /months/{yyyy-mm}/mark-sent-manually` `{sent_on, site_ids?}` | Saved → SentManually for the month |
| `GET /price-lists/vendors/{vendor_id}.xlsx?product_ids=` | Per-vendor price sheet: `SNO, Product Name, Price, GST %, HSN` (no qty) |

Errors use FastAPI's `{"detail": ...}` with 404 / 409 (state conflicts, duplicates) / 422 (validation). Every write goes through one transaction and writes `audit_log` rows.

### State rules

- Lines can only change while the requisition is `draft` (409 otherwise). Reopen first.
- `save` needs at least one line.
- `mark-sent-manually` only moves `saved` requisitions; drafts in the month are reported back, not touched.
- **Nothing in S1 sends email.** Save never sends.

## 7. Excel engine (openpyxl)

Built in code with explicit styles (`app/excel/styles.py`), not by copying a template file, so the output is deterministic and testable. Layout is the September / November 2026 file:

**Sheet `Product Details`**
- Row 1: `SBE STOCK REQUIREMENTS FOR THE MONTH OF NOVEMBER 2026`, merged A1:L1, bold, centred.
- Row 2: header `SNO | SITE | MONTH | VENDOR NAME | CHEMICAL / MATERIAL NAME | QTY REQ. | UNIT | PER COST | TAXABLE AMOUNT | GST | GST AMOUNT | TOTAL`, bold, filled, bordered, frozen below.
- Rows grouped by site (site `sort_order`), then vendor (name), then product name. `SITE` and `MONTH` merged vertically across the site group; `VENDOR NAME` merged across the vendor group inside the site. `SNO` runs 1..n continuously.
- `MONTH` is a real date cell with format `mmm-yy` (shows `Nov-26`). `GST` is a percent cell (`18%`). Money `#,##0.00`.
- Per-site subtotal row, then a bold **GRAND TOTAL** row (taxable, GST amount, total).
- Values, not formulas: the numbers equal what the app stored, and they show in Gmail / phone previews that do not calculate formulas.
- Column widths, thin borders on every cell in the table, A4 landscape, fit to width.

**Sheet `Vendor Details`**
- Row 1 `VENDOR DETAILS` merged. One block per vendor that appears on sheet 1, numbered: name (bold), then label/value rows `Address:` (one row per address line), `GSTIN:`, `Mail ID:`, `Phone:`, `Website:`, `Drug Licence:`, `Products:` — empty fields are skipped.

**No `Uniform Details` sheet.**

**Filename:** `STOCK REQUIREMENT-<SITES joined by ",">-<MON>-<YYYY>.xlsx`, e.g. `STOCK REQUIREMENT-TPJ BIO,MDU BIO,MS PFTR & PT,MS OFFICE-NOV-2026.xlsx`. Characters illegal in filenames are replaced with `-`.

**Price sheet:** one sheet `Price List`: title row with vendor name and date, header `SNO | Product Name | Price | GST % | HSN`, one row per product linked to the vendor (or the chosen subset). No quantities.

The review pane and the workbook are both built from the same `preview` structure, so what prem sees is what goes in the file.

## 8. Frontend (Next.js 14)

- `/stocks/requisitions?month=2026-11` — month picker; tabs = active sites with a badge for line count and status. Tab body: lines table (product, qty input, unit, vendor select, per cost, GST, taxable, GST amt, total, remove), **+ Add product** search box (debounced `GET /products?q=`), inline **New product** form when nothing matches, site totals. Buttons: **Generate Excel** (opens review pane + download), **Save**, **Reopen**.
- Month bar: **Review month** (consolidated preview), **Download HQ workbook**, **Mark sent manually**.
- `/stocks/products` — catalogue with aliases, vendors, current prices; change price with reason; price history.
- `/stocks/vendors` — vendor directory.
- `/stocks/price-lists` — pick vendor → download its price sheet.
- Data via TanStack Query; types hand-written in `src/lib/types.ts` for S1 (OpenAPI codegen once the API settles).
- UI primitives are shadcn-style components kept in `src/components/ui` (Tailwind + `cn()`), so the shadcn CLI can take over later without rewrites.

## 9. Auth (S1)

Single operator, LAN-only dev box. The API checks `Authorization: Bearer $API_TOKEN` when `API_TOKEN` is set. The browser never sees the token: Next.js proxies `/api/*` through a server route that adds it. NextAuth login (and later Google SSO) arrives with the foundation auth work before anything is exposed beyond the LAN.

## 10. Seed data (`python -m app.seed`, idempotent)

- Sites: MS PFTR & PT, MS OFFICE, TPJ BIO, MDU BIO, TPJ FORT, JTJ & KPD, SRR (others added in the UI).
- 14 vendors from the Nov-26 `Vendor Details` sheet (the sheet numbers 13 but lists 14 — two are numbered "3").
- 20 products from the Nov-26 `Product Details` sheet with unit, GST (18%; 5% for Co-Co Brooms and Cotton Cloth), vendor and price. Duplicates in the file are merged (`Surgical Gloves` is an alias of `Surgical Hand Gloves`); `Sterix-A Super` carries both HNR (₹100.60, preferred) and Transchem (₹30.00). HSN codes are blank in the source and must be filled in.

## 11. Testing

- Unit: money maths against Nov-26 rows; filename builder; search normaliser.
- Excel: generate from a fixture, re-open with openpyxl, assert sheet names, header, merges, SNO sequence, totals, no `Uniform Details`.
- API: full flow against a real Postgres (`TEST_DATABASE_URL`): create draft → add lines → duplicate rejected → price edit writes history → save → edit blocked → generate → download → mark sent manually.
- CI: ruff + pytest (Postgres service) + `next lint` + `tsc` + `next build`.

## 12. Running it

```bash
cp .env.example .env            # set POSTGRES_PASSWORD, API_TOKEN
docker compose -f infra/docker-compose.yml up --build
docker compose -f infra/docker-compose.yml exec api python -m app.seed
# web: http://localhost:3000/stocks/requisitions   api docs: http://localhost:8000/docs
```

The API container runs `alembic upgrade head` on start.
