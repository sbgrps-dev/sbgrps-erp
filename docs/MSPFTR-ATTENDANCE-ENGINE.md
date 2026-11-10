# MSPFTR — Attendance engine spec (MVP)

**Version:** 0.1 · 2026-11-09 · Confirmed by prem.

This spec turns one month at MSPFTR from a railway biometric file into the final `SBE_ATTENDANCE-*.xlsx` workbook, mirroring today's manual process.

## 1. Inputs

1. **Railway biometric workbook** (`RLWY_ATTENDANCE-MS_PFTR-<MONTH>-<YEAR>.xlsx`): 3 annexures for shift 1, shift 2 and shift 3 (watering). **Does not cover the full month** — only the date ranges the railways recorded. Missing dates are blank.
2. **Current employee master** (`Masterdata - <YEAR> - <MONTH> - MS PFTR.xlsx`) — authoritative roster, exit log and personal/bank/statutory details.
3. **Supervisor top-up list** (manual) — rows the office adds for people the railway sheet missed: recent joiners, rejoiners, car-wash staff. Today this is done inline in the output; the ERP will make it a first-class input (upload CSV/XLSX, or type in the UI).

## 2. Processing

```
Railway file ──┐
Master ────────┼─► Match on STAFF ID (fallback: fuzzy name within site)
Top-up list ───┘
            │
            ▼
   Day grid per employee: present / present_dummy / absent, per shift, per day
            │
            ▼
   Exception queue (unmatched, ambiguous, in-master-not-in-file, duplicate, >31 days)
            │
            ▼
   Payroll calc (section 4) ──► Preview + approve ──► Generate output workbook
```

### 2.1 Matching
- Primary key: `STAFF ID No` from the railway file ↔ `EMPLOYEE ID` in the master.
- Name variants (CHAMBARA vs CHAMBRA, OMONG vs OMOANG) are learned as **aliases** after the first confirmation.
- Ambiguous rows (same name, two possible IDs) are never applied automatically.

### 2.2 Day states
Store per employee × shift × day: `P`, `P-D` (dummy), or absent. P-D is not just a different mark — it reduces the payroll total.

### 2.3 Enrichment (manual top-up)
Rows added via top-up carry an `origin` tag chosen by the user: `rejoin`, `new_joiner`, `car_wash`, `missed_biometric`, `watering_only`, `other`. The origin tag is written into the output's `REMARKS` column automatically.

### 2.4 Exceptions raised each run
| Type | Meaning | Resolution |
|---|---|---|
| Unmatched | Row with ID/name not in master | Create provisional employee or link to existing |
| Ambiguous name | Name matches 2+ employees | User picks one |
| In master, not in file | Active employee missing in both biometric and top-up | Mark absent, or propose exit → approver |
| Duplicate | Same ID appears twice in the file | Merge or reject one |
| Day count > 31 | Sum across shifts > 31 after dummy subtraction | Review split |
| Partial month warning | Biometric range < 28 days | Confirm top-up list covers the rest |

## 3. Output workbook (`SBE_ATTENDANCE-MS_PFTR-<MONTH>-<YEAR>.xlsx`)

Three annexures identical in shape to the railway file, enriched with top-up rows. P-D marks are preserved. A `DUMMY` summary column is added to annexures II and III.

Then the **Payroll Consolidated Attendance Summary** sheet with the exact column order used today:

`SNO | NAME | STAFF ID | Ist Shift | IInd Shift | IIIrd Shift | Total WRK Days | Dummy | Total | OT | ACTUAL | SALARY | REMARKS`

And the **OT_Calc helper** block and **manpower reconciliation** block at the bottom, unchanged (see section 5).

## 4. Payroll calculation

For each employee with a day grid:

```
IstShift      = count(P on shift 1 days)
IIndShift     = count(P on shift 2 days)
IIIrdShift    = count(P on shift 3 days, any of the 3 trips present counts as 1)
Dummy         = count(P-D across all shifts × all days)
TotalWrkDays  = IstShift + IIndShift + IIIrdShift
Total         = TotalWrkDays − Dummy
ACTUAL        = min(Total, 31)
OT            = max(Total − 30, 0)
rate_per_day  = 525 if remarks contains 'CAR WASH' else 505     ← standard rule
base_pay      = min(ACTUAL, 30) × rate_per_day
ot_pay        = OT × 200
SALARY        = base_pay + ot_pay                                ← subject to manual override
```

**Manual overrides** (written to REMARKS, override SALARY):
- `NIGHT SHIFT — <N> days` → different formula, user types the final salary (e.g. Esakki Muthu ₹47,175 for 20 nights).
- `PROMOTED TO SUPERVISOR` → supervisor rate, user sets SALARY directly.
- Any REMARKS note that changes pay must be flagged so the approver sees it before sign-off.

Rate card lives at the **Contract** level (not hard-coded); admin can add a new rate type with an effective date without a code change.

## 5. Helper blocks (preserved byte-for-byte with today's template)

- **OT_Calc:** per-employee × 31-day 0/1 matrix, plus `r1 r2 r3` shift ranks, `ACTUAL`, `Ist WRK`, `IInd WRK`, `IIIrd WRK`, `Dummy`.
- **Manpower reconciliation:** constants come from the Contract entity:
  - PFTR formula: `2066 × 0.23`
  - CTS formula: `4405 × 0.2`
  - Supervisor: `3 × days_in_month`
  - Watering: `7492 / <watering_total>`
  - Saved manpower = required − actual.

## 6. Non-functional details

- **Partial biometric handling.** If the railway file covers only part of the month, show a yellow banner on review: "Biometric covers days X–Y; Z employees have top-up rows; W active employees have no record from either source."
- **Reprocessing.** Uploading the same railway file twice is detected by hash. The user can "replace with newer version" explicitly; the previous run is kept for audit.
- **Output idempotence.** Generating the workbook twice with the same inputs must produce byte-identical files so diffing against last month is possible.
- **Approval lock.** Once an approver signs off the month, the output is read-only. Later edits create a new revision with a reason.

## 7. Out of MVP scope (noted so the engine doesn't block them later)

- Annexures A–L generation (statutory and billing docs) — Phase 4.
- PF/ESI reconciliation — Phase 3.
- Direct biometric machine integration — later.

## 8. Still open

- **Rejoiner model.** When the same person returns under a new EMPLOYEE ID, should the ERP link both IDs to one Person entity, or keep them as separate records (today's behaviour)? Default in the current PRD: one Person, many employment spells. Confirm with prem.
- **Night shift premium formula.** Currently a manual override. Worth formalising? Needs a rate table if yes.
- **Attendance Bonus column.** All zero in Oct 2026 — is it ever used? If not, drop from UI; if yes, define the rule.
