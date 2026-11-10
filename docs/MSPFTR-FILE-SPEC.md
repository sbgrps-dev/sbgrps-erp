# MSPFTR — real file shapes (October 2026 samples)

**Purpose:** record the actual column structure so the import engine can be built against it. All sheet references below are to the October 2026 files in Drive.

## 1. Railway biometric input — `RLWY_ATTENDANCE-MS_PFTR-OCTOBER-2026.xlsx`

One workbook, three annexures stacked:

### Annexure I (Shift 1) and Annexure II (Shift 2)
Columns: `SL NO | NAME | STAFF ID No | 1 | 2 | ... | 31 | No of Day Present`

- Cell marks: `P` = present, blank = absent.
- Staff ID range in Oct 2026: 100–215.
- Totals row + "Staff Present on the day" row at the bottom.

### Annexure III (Shift 3 = carriage watering)
Columns: `SL NO | NAME | STAFF ID No | 1 (×3) | 2 (×3) | ... | 31 (×3) | WRKNG DAYS`

- Each day column is split into **three sub-columns** representing three water-rake trips in that day.
- Marks: `P` or `P-D`. `P-D` denotes a different pay category ("Dummy") — it's counted separately on the output.

## 2. Employee master — `Masterdata - 2026 - October - MS PFTR.xlsx`

Three stacked sections in one sheet:

### 2.1 Active roster (top)
Columns: `SL.NO | EMPLOYEE ID | EMPLOYEE NAME | FATHER/HUSBAND NAME | DESIGNATION | DOB | GENDER | AADHAR | CONTACT NUMBER | PF | ESI | BANK ACC.NO | IFSC CODE | BRANCH | Alternate A/c Name | No of days | Additional Shift (Dummy) | OT DAYS | OT wages | Attendance Bonus | wages per day | Total wages | Remarks`

- **Aadhaar is stored** (12-digit numbers).
- `Alternate A/c Name` means salary is routed through someone else's bank account (common pattern — many employees share proxy accounts; dominant IFSC is `KKBK0000463 ADYAR`).

### 2.2 LEFT SITE (middle) — ~90 historical records, same columns plus a `MS PFTR` tag column
- Duplicates by name are allowed (rejoiners get new IDs).
- Remarks column carries real status hints: `left`, `Rejoning`, `USED FOR <name>`, `WAGES PER DAY 500`, `CAR WASH`, `ESIC NO UPDATE`, `APPROVAL PENDING` (PF not registered), `Aadhar issue`, `acc expirt`.

### 2.3 DATE OF EXIT (bottom) — authoritative exit log, grouped by month
Months present: Sept 2025 → Sept 2026.

## 3. SBE monthly output — `SBE_ATTENDANCE-MS_PFTR-OCTOBER-2026.xlsx`

Mirrors the three railway annexures but is **enriched** and adds a payroll sheet.

### 3.1 Enrichment — new rows that are in the output but not in the railway input
Examples from Oct 2026: DHANAM, INDIRA R, PRADEEP MEGEND, KRISHNA HEMBRAM, SUNDAR, RAMRAI HEMBRAM, BONJI HEMBRUM, GULAM OMOANG, LUGUDHI HEMBRAM, GUNA, THENMOZHI, R JAYANTHI, VIJAYA, DURGA B, S RENUGA DEVI, N AMMU, M DEVI.

These are CAR WASH staff, rejoiners, new joiners and others billed outside the railway sheet. **[OPEN]** Where do these rows come from today — SBE's own biometric, a supervisor-entered sheet, or manual typing?

### 3.2 Annexures II and III get an extra `DUMMY` column that totals P-D marks.

### 3.3 Payroll Consolidated Attendance Summary (final sheet)
Columns: `SNO | NAME | STAFF ID | Ist Shift | IInd Shift | IIIrd Shift | Total WRK Days | Dummy | Total | OT | ACTUAL | SALARY | REMARKS`

- `Total = WRK − Dummy` capped at 31.
- `OT = Total − 30` (any day over 30 counts as overtime).
- `ACTUAL = min(Total, 31)` = days paid base rate.
- Salary formula (Oct 2026 reference): base ≈ ₹505/day × up to 30 days (= ₹15,150 for a full month), plus OT days at ₹200/day. Manual overrides in REMARKS: night shift (`ESAKKI MUTHU` 20 night shifts = ₹47,175), promotions (`SASI PROMOTED TO SUPERVISOR` = ₹24,300), CAR WASH flag, etc.
- Attendance Bonus column present, all zeros this month.

### 3.4 Manpower reconciliation block (bottom of payroll sheet)
Compares actual manpower against the Letter of Award formulas:
- `PFTR 2066 × 0.23` → required
- `CTS 4405 × 0.2` → required
- Supervisor: `3 × 31`
- Watering manpower: `7492 / 442` → ratio
- Saved manpower = Required − Actual

### 3.5 OT_Calc helper block
Per-employee × 31-day 0/1 matrix plus `r1, r2, r3` rank columns (daily rank across the three shifts), then `ACTUAL`, `Ist WRK`, `IInd WRK`, `IIIrd WRK`, `Dummy`. This helper is what feeds the payroll summary.

## 4. Statutory / billing annexures (A–L) — 12 more workbooks per month
`MS_PFTR-ANNEXURE A..L` for October and November 2026 exist in Drive, sizes 13–80 KB. These are Form XVII, wage register, PF/ESI statements and billing annexures, all driven off the payroll summary.

> Billing is out of MVP scope; these are listed here so the import spec can be designed with the later generator in mind.

## 5. Implications for the ERP

1. **One import = three annexures.** The MSPFTR import profile must know how to split a railway workbook into shifts 1, 2 and 3, and handle Annexure III's 3-sub-column layout.
2. **Matching key is `STAFF ID No`.** It's the biometric/staff ID that already exists on both the railway sheet and the master. Names drift (CHAMBARA vs CHAMBRA, CHAMBARA OMONG vs CHAMBARA OMOANG) so names are the fallback only.
3. **`P-D` counts separately.** The internal data model should store `present | present_dummy | absent` per day, not a single boolean.
4. **Employees in the output but not in the railway input** are the source of today's errors — the system has to make this explicit, not hide it. Each such row needs an origin tag (e.g. CAR WASH, rejoiner, SBE-only shift).
5. **Exits are authoritative in the master's bottom section**, not derived from a missing attendance row alone. The lifecycle flow in the PRD (missing → propose exit → approve) matches this exactly.
6. **Aadhaar is already stored.** The ERP will have to protect it: encryption at rest, masking in the UI, logged unmasking.
7. **Rejoiners get new IDs.** The employee entity needs to support multiple historical allocations/IDs linked back to one person, or the ERP has to replicate the current "new row per rejoin" behaviour. **[OPEN]** Which approach does prem want?
8. **Salary rules are per-employee and manual.** Night shift premium, promotions and CAR WASH are overrides, not formulas. The payroll module (later) will need a per-employee rate table with effective dates and a free-text remark that lands in the output.
9. **Manpower reconciliation block** uses contract constants (2066, 4405, 7492, 3 shifts × 31). These belong to the Contract entity, not the Site entity.
