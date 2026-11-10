# SBGRPS ERP — Stocks module PRD

**Version:** v0.3 · 2026-11-10 · Single-user mode. Based on prem's master draft Module 06 plus the September and November 2026 real files in Drive.

> We stay inside **v0.x** until the app is handed over. Each revision bumps the point number (v0.1, v0.2, v0.3 …). v1.0 = first released, handed-over app. No "V2/V3/V4" labels in this document.

## 1. Why stocks first

- One Excel workbook per month per site today, consolidated by hand into one master requisition and emailed to vendors.
- Fewest actors, no statutory consequences.
- Forces the organisation / site / vendor / product entities into existence — every later module (attendance, PF/ESI) reuses them.
- A single clean "generate and send" step saves prem real time every month.

## 2. The flow prem wants (decided 2026-11-10)

> prem opens the app → clicks a site → searches for a product → enters the quantity → the system automatically prepares the Excel and opens it for review → **Save**. Nothing is sent automatically. Sending is a separate button, only when prem clicks it; some months prem will send manually outside the app and that must stay possible.

No site reps, no approvers, no current-stock entry, no uniforms. One operator (prem) doing the whole thing.

## 2.1 Two email flows — different audiences, different buttons

The app does **not** email vendors the monthly requisition. The flows are:

**Flow A — Send requisition to higher authority (for PO issuance).**
- Recipient: **vidyaparam@sbgrs.com** (higher authority at SB Group).
- Attachment: the full consolidated Excel in the September two-sheet layout, **all sites together**.
- Purpose: they review and issue the actual Purchase Order. The ERP does not issue POs.
- Trigger: prem clicks **Send requisition to HQ** on a Saved requisition. The app drafts the email; prem reviews and sends.

**Flow B — Send price verification sheet to vendors.**
- Recipient: each vendor (one email per vendor).
- Attachment: a per-vendor price sheet with columns **SNO | Product Name | Price | GST | HSN**. Quantities are **not** on this sheet; it's a price-check, not an order.
- Purpose: vendor confirms or revises prices. prem accepts the reply, which updates `ProductPrice` (new history row).
- Trigger: prem clicks **Send price list to vendors**. Can be done any time, independent of a monthly requisition.

Both flows always need prem's explicit click. Save never sends.

## 3. Actors

| Actor | Role in v0 (pre-handover) |
|---|---|
| prem (Operator) | Picks site, searches product, enters qty, saves the requisition, optionally sends it to HQ, optionally sends price list to vendors |
| Higher authority (vidyaparam@sbgrs.com) | Receives the saved requisition Excel and issues the PO outside the app |
| Vendor (external) | Receives a price-verification sheet; may reply with revised prices |

No separate site-rep or approver role before release. Site Reps (view-only) come later; captured in §14.

## 4. Sites (as seen in the real files)

- **MS PFTR & PT** — one site (Chennai Egmore CTS section). "MS PFTR" and "MS PT" refer to the same site; display as `MS PFTR & PT`.
- **MS OFFICE** — SBGRPS Egmore internal office; separate from MS PFTR & PT. Supplies are office consumables (Harpic, room freshener, polythene bags).
- **TPJ BIO**, **MDU BIO** — bio-toilet cleaning sites (Tiruchirappalli and Madurai).
- **TPJ Fort**, **JTJ & KPD**, **SRR** and the remaining live sites can raise requisitions too; the Sep 2026 file already shows JTJ & KPD and SRR, so the MVP must support any of the 13 live sites.

Site is a free text display label stored once; "MS PFTR & PT" is one row in the site table.

## 5. In scope (v1)

- Vendor directory (13 vendors preloaded from the real files).
- Master product catalogue with: name + aliases, unit, HSN, GST%, approved vendor(s), current per-unit price, price history.
- Per-month, per-site requisition: operator picks site, searches product, enters qty, system fills unit / price / GST / taxable / GST amount / total automatically.
- Auto-generated Excel in the **September template** (two sheets: `Product Details`, `Vendor Details`; **no `Uniform Details` sheet** — omitted per prem).
- Review pane that mirrors the Excel before saving.
- **Save** button — stores the requisition and its generated Excel version. Sends nothing.
- **Send requisition to HQ** button — drafts an email to `vidyaparam@sbgrs.com` with the full consolidated Excel attached, prem sends after review.
- **Send price list to vendors** feature (independent of the monthly requisition) — per-vendor price-verification sheet (`SNO | Product Name | Price | GST | HSN`).
- Capture vendor price replies as attachments on the price-list sent-record; accepting a reply writes a new `ProductPrice` row.
- History of past months' requisitions, HQ emails, and price-verification emails.

## 6. Out of scope

- **Uniform / shoe size breakdowns** (the "Uniform Details" sheet) — dropped per prem. Uniforms, if ordered, go as single lines on `Product Details`.
- **Current / opening stock column** — dropped per prem. The September `Product Details` sheet doesn't carry it either (that column only lived on the raw "STOCK NEED" input). Operator enters only the required quantity.
- **Direct ordering to vendors from the app** — vendors are never emailed the requisition; HQ issues the PO.
- Multi-user, approvals, mobile site-rep UI.
- Goods receipt, delivery tracking, inventory consumption, payments, PO documents (issued by HQ).
- Automatic vendor-reply parsing — the reply is attached to the price-list record, prem reads it and updates prices by clicking Accept.

## 7. The September "beautifully organised" template is the target output

Two sheets:

### Sheet 1 — `Product Details`
Columns: `SNO | SITE | MONTH | VENDOR NAME | CHEMICAL / MATERIAL NAME | QTY REQ. | UNIT | PER COST | TAXABLE AMOUNT | GST | GST AMOUNT | TOTAL`

- Rows grouped by `SITE`, then `VENDOR`. Site and vendor cells merged/blank for subsequent rows in the same group.
- SNO auto-numbered by the system.
- Per-line totals and a grand total at the bottom.

### Sheet 2 — `Vendor Details`
One block per vendor present on sheet 1: name, address, GSTIN, email, phone(s), website, drug licence (where applicable), products supplied.

### No sheet 3
`Uniform Details` is not generated.

## 8. User experience (the exact steps)

1. prem opens the app → **Stocks** → **Requisitions** → **November 2026** (or picks a month).
2. Grid shows one tab per site: `MS PFTR & PT`, `MS OFFICE`, `TPJ BIO`, `MDU BIO`, `JTJ & KPD`, `SRR`, `TPJ Fort`, … (every live site).
3. In a site tab, prem clicks **+ Add product**, searches ("apc", "gloves", "sterix"), picks a product.
4. Inline fields appear: `qty`, auto-filled `unit`, `vendor` (default = the product's preferred vendor; dropdown to switch to another approved vendor), auto-filled `per cost`, `GST %`, `taxable`, `GST amount`, `total`.
5. Can edit qty, per cost (saved as a new price in history with a reason), or vendor.
6. When done, prem clicks **Generate Excel**. System builds the two-sheet workbook in the September layout, and opens a review pane with:
   - the Product Details rows exactly as they'll appear in Excel
   - the Vendor Details block for every vendor cited
   - grand totals (taxable, GST, total)
7. If something looks wrong, prem edits a row and clicks Generate again.
8. Happy → **Save**. The requisition and this Excel version are stored. Nothing is sent.
9. When ready, prem opens the saved requisition and clicks **Send to HQ**. The app drafts an email to `vidyaparam@sbgrs.com` with the full consolidated Excel attached; prem reviews and sends. Some months prem will send manually from Gmail instead; that's fine — he marks the saved requisition "sent manually" so history is complete.
10. Separately, whenever prem wants vendors to re-confirm prices, he opens **Price verification** → picks vendors → clicks **Send price list to vendors**. The app drafts one email per vendor with a price sheet (`SNO | Product Name | Price | GST | HSN`) attached. Vendor replies are captured and prem accepts them to update prices.

## 9. Functional requirements

### 9.1 Vendor directory
- FR-VEN-1: Fields: name, address, GSTIN, phone(s), email(s), website, drug licence (nullable), products supplied, active flag.
- FR-VEN-2: Preload the 13 vendors from the Nov 2026 file. Admin UI can add / edit.

### 9.2 Product catalogue
- FR-PRD-1: Fields: code, name, aliases (list of strings), unit (free text), HSN, GST rate %, status.
- FR-PRD-2: Each product has one or more approved vendors; each `(product, vendor)` pair carries a current price and a `price_history` list.
- FR-PRD-3: Aliases let `STERIX-A super`, `STERIX A SUPER`, `STERIX SUPER` all match one product; search is case-insensitive and alias-aware.
- FR-PRD-4: Admin can add a new product mid-flow without leaving the requisition; the new product shows up in the master catalogue.

### 9.3 Requisition
- FR-REQ-1: One requisition per `(site, month)`. Creating a month creates a blank requisition per site on demand.
- FR-REQ-2: A line is `(product, qty, vendor, per_cost_snapshot, gst_rate_snapshot, taxable, gst_amount, line_total, notes)`.
- FR-REQ-3: Validations: qty > 0; no duplicate `(product, vendor)` line within one site requisition; product must have an approved vendor (if not, operator either picks one or adds a vendor).
- FR-REQ-4: Edits to per-cost after save create a new `ProductPrice` row (price history) with a reason.
- FR-REQ-5: Grand totals computed live in the UI and written into the workbook.

### 9.4 Excel generation
- FR-OUT-1: Generator produces the two-sheet workbook in the September template, byte-for-byte compatible with what prem sends today (column widths, header row, merged cells for Site and Vendor groups, GST formatting, ₹ totals).
- FR-OUT-2: Filename pattern: `STOCK REQUIREMENT-<SITE>-<MONTH>-<YEAR>.xlsx` for a single site, or `STOCK REQUIREMENT-<SITES CSV>-<MONTH>-<YEAR>.xlsx` for multi-site.
- FR-OUT-3: Re-generating the same requisition produces a new version; previous version kept for audit.
- FR-OUT-4: Review pane shows the exact table before download/send.

### 9.5 Send requisition to HQ
- FR-HQ-1: On a Saved requisition, prem clicks **Send to HQ**. The app drafts one email to `vidyaparam@sbgrs.com` with the full consolidated Excel (all sites, September layout) as the attachment.
- FR-HQ-2: Subject template: `SBGRPS — Stock Requisition — <Month> <Year>`. Body configurable.
- FR-HQ-3: prem reviews and clicks Send. Sent record stored with timestamp and message-ID.
- FR-HQ-4: Alternative path: prem sends manually from Gmail. He can mark the saved requisition **Sent manually** with a date so history reflects reality.
- FR-HQ-5: Nothing is auto-sent. **Save never sends.**

### 9.6 Send price list to vendors (price verification)
- FR-PV-1: Independent of any monthly requisition. Opens from a **Price verification** screen that lists vendors and the products linked to each.
- FR-PV-2: prem picks one vendor or many, picks which of their products to include, clicks **Send price list**.
- FR-PV-3: Per-vendor draft email with an Excel attachment containing: `SNO | Product Name | Price | GST % | HSN`. **No quantities.** Purpose is pure price verification.
- FR-PV-4: prem reviews and sends. Sent records stored with timestamp and message-ID.
- FR-PV-5: Replies (same thread, or manually linked) are attached to the sent record. prem compares vendor's reply against stored prices and clicks **Accept** per line; accepted lines create new `ProductPrice` rows (old prices retained in history).
- FR-PV-6: Rejected/ignored lines leave prices unchanged.

### 9.6 History
- FR-HIS-1: Past month's requisitions are listable and downloadable in either single-site or multi-site layout.
- FR-HIS-2: Every change writes an audit row (operator, field, old, new, reason, when).

## 10. Non-functional

- **Operator device**: desktop web (prem said he opens the app and clicks). Mobile-friendly later.
- **Language**: English.
- **Access**: only prem logs in for now. Second user later.
- **Data**: multi-tenant-ready in the model, but one tenant (SBE) in the MVP.

## 11. Success metrics

- Minutes to produce one monthly consolidated workbook (baseline **[OPEN]**: how long does it take prem today?).
- Number of manual edits to the generated Excel before it's sent.
- Zero numeric mismatches against October 2026 baseline (same input → same totals).

## 12. Risks

| Risk | Mitigation |
|---|---|
| Different sites have slightly different product names | Aliases on products, learned once |
| Vendor emails bounce | Delivery/failure log, retry queue |
| Price drift between stored and real | Easy price edit → new history row; vendor reply flow for official updates |
| Operator wants to see prior months' numbers | History + export in old layout |

## 13. Still open (nice to confirm, not blocking)

1. **Baseline time.** Roughly how long does it take today to produce one month's consolidated workbook?
2. **Second user.** Who else, if anyone, should be able to log in later — attendance staff, your co-builder, SB Group IT after handover?
3. **MS OFFICE products.** Nov 2026 shows this site needs Harpic, soap oil, polythene, room freshener, urinal cubes, hand wash, hand gloves, scent. Should MS OFFICE products be a separate catalogue, or share the master catalogue with a flag?
4. **New product on the fly.** When a vendor introduces a new chemical mid-month, add it inline or go to Settings → Products first? I'd make inline-add the default.

## 14. Planned later (still pre-release) (same version, not now)

Still pre-release — captured here so the data model and UI keep room for them:

- **Site Rep (view-only)** access: each site supervisor logs in and sees their own site's current requisition and past months, read-only. If something looks wrong (missing product, qty too low or too high), they call prem and he updates. Writes still go through prem.
- Then: Site Rep can **raise a change request** on a line (comment + proposed qty) that prem accepts or rejects — still no direct write from the site.
- Planned later (still pre-release): multi-user central office if needed, structured vendor-reply parsing, delivery tracking against the HQ-issued PO.

## 15. Dependencies

- Minimal org/site table (already in DATA-MODEL.md).
- Email provider access (same account as later attendance email ingestion).
