# SBGRPS ERP — Product Requirements Document

**Version:** 0.2 (draft) · **Date:** 2026-11-09 · **Owners:** prem + co-builder · **Project account:** sbgrps.dev@gmail.com
**Source:** prem's master business-requirements draft v1.0 ([source-master-draft-v1.md](source-master-draft-v1.md)) plus answers given on 2026-11-09.

> Items marked **[OPEN]** are still waiting on an answer or on sample files.

---

## 1. Summary

SBGRPS (Shree Balaji Groups) needs one central, **semi-automated** system that replaces the repetitive Excel work behind workforce administration: collecting attendance from many sites, matching names to the employee master, tracking joiners and leavers, and reconciling PF/ESI.

The first release covers **Shree Balaji Enterprises (SBE)** only, starting with the **MSPFTR** site. The long-term goal is one ERP for all four group companies.

**Core idea:** one source of truth for employee data, configurable import engines (not one script per site), and a human approval step for anything uncertain.

## 2. Organisation

| Entity | In scope now? |
|---|---|
| Shree Balaji Enterprises (SBE) — railway cleaning contracts | **Yes (MVP)** |
| Shree Balaji Industries | Phase 6 |
| Shree Karuppasamy Transports | Phase 6 |
| PKR Automotive Limited | Phase 6 |

### 2.1 SBE sites

**Live (13):** MSPFTR (platform and train-rake cleaning), PTC (pass-through train cleaning, Egmore), JTJ (Jolarpettai), KPD (Katpadi), MAS (Chennai Central), SRR (Shoranur), MDU (Madurai), TEN (Tirunelveli), TN (Tuticorin), RMM (Rameswaram), TPJ (Tiruchirappalli), TPJ Fort, VM (Villupuram).

**Waiting list, not acquired:** BBQ, GSN, TBM. The system must allow adding them later by configuration.

**Headcount:** 9 to 400 per site, average about 60. MAS is the largest at 300+. Total SBE headcount **[OPEN]**.

**Who runs it today:** 2–3 office staff. prem handles attendance for JTJ, KPD, SRR, TEN, MDU, TN, RMM, TPJ, TPJ Fort and VM, and both attendance and billing for MSPFTR. Ownership of PTC and MAS **[OPEN]**.

## 3. Problem

Each month the office:
- receives attendance in different formats (biometric Excel/CSV exports, hand-made Excel sheets with names and day totals), mostly by email;
- matches names by hand against the employee master, where spellings differ;
- works out who joined and who left, and chases missing details for new joiners;
- compares PF/ESI portal data with internal records by hand;
- copies the same employee data into several workbooks (attendance, Form XVII, wage register and others).

This is slow, repetitive and error-prone, and errors can carry statutory consequences.

## 4. Goals and non-goals

### Goals for the MVP
1. One verified **employee master** for SBE, with a unique ID per employee and a history of status and site changes.
2. Import the **MSPFTR biometric export**, match every row to the master, and flag anything uncertain.
3. Detect **new joiners** (create a provisional record) and **possible exits** (send to review, never auto-exit).
4. Produce the monthly **attendance workbook** in the existing template, after review.
5. Add the remaining live sites' formats one at a time, through configuration.

### Non-goals for the MVP
- Billing and document generation (complex, needs its own design; discussed later).
- Multi-document generation from ~20 common fields (only relevant if BBQ, GSN or TBM are acquired).
- PF/ESI reconciliation (next phase, right after attendance).
- Procurement, vendors, inventory, payroll calculation.
- WhatsApp, a mobile app, direct biometric or portal integrations.
- Other group companies.

## 5. Product principles (non-negotiable)

1. **One source of truth.** The database is authoritative; Excel files are inputs and outputs.
2. **Semi-automation.** Automate the repetitive work; people approve important decisions.
3. **Accuracy first.** No silent guesses. An uncertain match goes to review.
4. **Excel compatibility.** Keep existing templates, formulas and layouts.
5. **Configure, don't hard-code.** A new site means a new import configuration, not new code.
6. **Exception-driven.** Clean rows go straight through; only problems reach a person.
7. **Full traceability.** Every critical change records who, what, when, why and the source file.
8. **Never delete history.** Exited employees and old records stay retrievable.

## 6. Users and roles

See [PERSONAS.md](PERSONAS.md) for detail.

| Role | MVP? | Does |
|---|---|---|
| Group Super Admin | Yes | Sets up companies, sites and users; full access |
| Central HR/Admin (attendance processor) | Yes | Uploads files, resolves matches, runs monthly attendance |
| Approver | Yes | Approves exits, master-data corrections and final attendance |
| Site Representative | Later | For now sites keep emailing files; login comes in a later phase |
| Auditor / Read-only | Later | Views history |
| Company Admin, Accounts/Billing, Procurement | Later phases | |

Rule: nobody approves their own critical change; for example, the person who proposes an exit cannot also approve it. **[OPEN]** With 2–3 people, is a separate approver realistic, or should prem/the Super Admin approve?

## 7. Scope and roadmap

| Phase | Content | Status |
|---|---|---|
| **1 — Foundation (MVP)** | Company/site/contract setup, users and roles, employee master, employee lifecycle, Excel import engine, audit log | **MVP** |
| **2 — Attendance (MVP)** | Per-site import configuration, matching, joiner/exit detection, exception queue, attendance workbook output; MSPFTR first, then other sites; then email ingestion from deivanayagam.k@sbgrps.com | **MVP** |
| 3 — PF/ESI reconciliation | Portal report ingestion, multi-field identity matching, discrepancy review, approved corrections, summary email | Next |
| 4 — Billing and documents | Template library, field mapping, calculations, previews, versions | Later, needs its own spec |
| 5 — Procurement | Products, vendors, requisitions, GST, POs | Later |
| 6 — Group expansion | Other three companies, inventory, payroll, reporting | Later |

### 7.1 MVP build order
1. Employee master: import the existing master sheet(s), find duplicates and gaps, and get a clean baseline signed off.
2. MSPFTR biometric import, tested against **past months** whose outputs are already approved.
3. Exception queue and review screens.
4. Attendance workbook output in the existing template.
5. Next site formats, one at a time (order **[OPEN]**).
6. Email ingestion from the mailbox.
7. Automatic "send missing joiner details" email.

## 8. Functional requirements (MVP)

### 8.1 Organisation setup
- FR-ORG-1: Create a group, companies, sites (code, name, location, company) and contracts (number, client, start and end dates).
- FR-ORG-2: Each site has a status (Live, Waiting list, Closed) and an attendance-source configuration.
- FR-ORG-3: Users get roles scoped to company and/or site.

### 8.2 Employee master
- FR-EMP-1: Each employee has a unique internal ID that never changes.
- FR-EMP-2: Fields: name, gender, DOB, parent name, mobile, address, DOJ, designation, company, site, contract, bank details, UAN/PF, ESI, status, exit date and reason. Aadhaar **[OPEN]**: whether to store it at all.
- FR-EMP-3: Status is one of Provisional, Active, Exited. Changes are logged with date, user and reason.
- FR-EMP-4: Site-allocation history (an employee can move between sites).
- FR-EMP-5: Bulk import from the existing master Excel, with duplicate detection and a review step before anything is committed.
- FR-EMP-6: Sensitive fields (bank account, identity numbers) are masked by default and every view of them is logged.
- FR-EMP-7: Records are never hard-deleted.

### 8.3 Attendance import
- FR-ATT-1: Upload an attendance file (xlsx/csv) and tag it with site and month (auto-detected where possible, confirmed by the user).
- FR-ATT-2: The original file is stored unchanged.
- FR-ATT-3: Per-site **import profile**: sheet, header row, ID column, name column, date/punch columns, status codes, working-day rule.
- FR-ATT-4: Convert to a standard internal structure (employee, date or month, days present, source row).
- FR-ATT-5: The same file uploaded twice is detected (by hash); reprocessing is explicit and versioned.
- FR-ATT-6: Job status: Received → Processing → Awaiting review → Approved, or Failed with a reason.

### 8.4 Matching
- FR-MAT-1: Match by employee or biometric ID first; fall back to fuzzy name matching within the same site.
- FR-MAT-2: Each match gets a confidence label: Exact, Probable, Ambiguous or Unmatched. Only Exact is applied automatically. **[OPEN]** Should Probable also auto-apply?
- FR-MAT-3: When a person confirms a name variant, it is saved as an alias so the same row matches automatically next month.

### 8.5 Exceptions and lifecycle
- FR-EXC-1: Exception types: unmatched row, ambiguous match, in master but missing from attendance, duplicate row, invalid day count (for example above the days in the month), employee allocated to another site.
- FR-EXC-2: Each exception has an ID, site, month, type, priority, assignee, status and resolution note.
- FR-EXC-3: Unmatched row → the user links it to an existing employee or creates a **Provisional** employee.
- FR-EXC-4: Missing from attendance → the user marks *still active (absent)* or proposes *exit* with a date and reason; an approver confirms.
- FR-EXC-5: Provisional employees stay flagged until mandatory fields are filled and approved.

### 8.6 Output
- FR-OUT-1: Generate the monthly attendance workbook in the **existing template** (layout, formulas, formatting, employee order kept).
- FR-OUT-2: Preview before approval; once approved, the output is versioned and read-only. Changes after that create a new revision.
- FR-OUT-3: Monthly summary per site: headcount, joiners, exits, open exceptions.

### 8.7 Email ingestion (end of MVP)
- FR-MAIL-1: Read attachments from deivanayagam.k@sbgrps.com (mail provider and access method **[OPEN]**).
- FR-MAIL-2: Accept only known senders mapped to sites; anything else goes to a manual triage list.
- FR-MAIL-3: Draft an email to the site sender asking for missing joiner details; a person approves before it is sent.

### 8.8 Dashboard
- Per site and month: file received or not, processing status, open exceptions, joiners, exits.

## 9. Non-functional requirements

| Area | Requirement |
|---|---|
| Accuracy | No silent failures or guesses; every automated decision can be explained |
| Scale (MVP) | About 14 sites, under 2,000 employees (estimate **[OPEN]**), a few concurrent users; must handle MAS (300+ rows) quickly |
| Security | Role-based access, HTTPS, encryption at rest for sensitive fields, masking, audit of sensitive views |
| Privacy | Comply with India's DPDP Act 2023; collect only the identity data that is needed |
| Audit | Old value, new value, user, time, reason and source file for every critical change |
| Backup | Daily database and file backups; restore tested |
| Usability | Desktop web for office staff; English **[OPEN]** for other languages |
| Handover | Documented code, deployment and runbook so SB Group can own it |

## 10. Success metrics

- Time to process one site's monthly attendance, compared with the manual baseline (baseline **[OPEN]**: how long does MSPFTR take today?).
- Share of rows matched automatically with no correction.
- **Zero** mismatches when compared with already-approved historical months.
- Number of sites live on the system.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Messy existing master data | Clean-up and sign-off before go-live |
| Every site's format is different | Configurable import profiles; add sites one at a time |
| Wrong fuzzy match records attendance for the wrong person | Only exact matches auto-apply; aliases are learned from human decisions |
| Complex Excel templates break when generated | Fill the template rather than rebuild it; compare output with real past files |
| Mailbox access depends on the provider and company IT | Manual upload works first; email comes last in the MVP |
| Sensitive PII | Masking, access logs, minimal collection |

## 12. Open questions

1. Total SBE headcount, and who handles PTC and MAS.
2. Order of sites after MSPFTR.
3. Is a separate approver realistic with 2–3 staff?
4. Do employees and biometric records share an ID today?
5. Is Aadhaar needed in the system?
6. Mail provider for deivanayagam.k@sbgrps.com (Google Workspace, Zoho, other) and who can grant API access.
7. Tech stack and hosting (after reviewing the sample files).
8. Who on the SB Group side signs off requirements and accepts the handover.
9. Target date for the MSPFTR pilot.

## 13. Dependencies (needed before build)

- Sample files: MSPFTR biometric export, one other site's attendance Excel, employee master, one PF/ESI report, the monthly output templates, all anonymised.
- 2–3 past months of MSPFTR input and approved output, used as test cases.
