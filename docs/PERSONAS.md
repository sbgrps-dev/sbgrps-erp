# SBGRPS ERP — User roles and personas

**Version:** 0.1 · 2026-11-09 · Based on the master draft v1.0 and prem's answers. Names below describe roles, not real staff.

## MVP personas

### 1. Attendance processor (Central HR/Admin)
- **Who:** One of the 2–3 office staff, or prem for the sites he handles (JTJ, KPD, SRR, TEN, MDU, TN, RMM, TPJ, TPJ Fort, VM, MSPFTR).
- **Does monthly:** Collects attendance files from email, matches names to the master, finds joiners and leavers, fills the attendance workbook.
- **Pain today:** Different format per site, name spellings that don't match, hours spent copying between sheets, chasing site staff for new joiners' details.
- **Needs from the ERP:** Upload a file and see at once what matched and what didn't; a short list of problems to fix; the final workbook in the same format as today.
- **Tools:** Desktop, Excel, email.
- **Must not:** Approve their own exit or master-data correction.

### 2. Approver
- **Who:** A senior office person or management (to be named; with 2–3 staff this may be prem or the Super Admin).
- **Does:** Confirms employee exits, approves corrections to the master, signs off the monthly attendance before it goes out.
- **Needs:** A clear view of what changed, why, and the source file; approve or reject in one place.

### 3. Group Super Admin
- **Who:** prem and the co-builder during development; an SB Group IT or admin person after handover.
- **Does:** Sets up companies, sites (including waiting-list sites like BBQ, GSN, TBM), contracts, users and roles, and per-site import profiles.
- **Needs:** Add a new site or a new attendance format without a developer.

## Later-phase personas

### 4. Site Representative (supervisor at a station)
- **Who:** Supervisor at a site such as MAS (300+ staff) or RMM (small).
- **Today:** Emails the biometric export or a hand-made Excel sheet; gets asked for new joiners' details.
- **Later:** Logs in (likely on a phone) to upload attendance, fill joiner details and raise stock requisitions.
- **Must not:** Change PF/ESI numbers or approve anything statutory.

### 5. PF/ESI reconciler (Phase 3)
- Receives the monthly portal data by email and reviews mismatches side by side; approves corrections to the master.

### 6. Accounts/Billing user (Phase 4)
- Prepares monthly billing workbooks (today prem does this for MSPFTR). Needs exact, auditable figures.

### 7. Procurement user (Phase 5)
- Reviews site requisitions, confirms vendor prices, issues POs.

### 8. Auditor / read-only
- Views records, history and documents; changes nothing.

### 9. Company Admin (Phase 6)
- Manages one group company (for example Shree Karuppasamy Transports) with no access to the others.

## Permission matrix (MVP)

| Action | Super Admin | Processor | Approver | Site Rep (later) | Auditor |
|---|:-:|:-:|:-:|:-:|:-:|
| Configure company/site/import profile | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage users and roles | ✅ | ❌ | ❌ | ❌ | ❌ |
| Upload attendance | ✅ | ✅ | ❌ | ✅ (own site) | ❌ |
| Resolve match exceptions | ✅ | ✅ | ✅ | ❌ | ❌ |
| Create provisional employee | ✅ | ✅ | ✅ | ✅ (own site) | ❌ |
| Propose exit / master correction | ✅ | ✅ | ✅ | ❌ | ❌ |
| Approve exit / correction | ✅ | ❌ | ✅ (not own) | ❌ | ❌ |
| Approve final attendance | ✅ | ❌ | ✅ | ❌ | ❌ |
| View unmasked bank / ID numbers | ✅ (logged) | ❌ | ✅ (logged) | ❌ | ❌ |
| View audit log | ✅ | ❌ | ✅ | ❌ | ✅ |
