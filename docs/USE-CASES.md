# SBGRPS ERP — Use cases (MVP)

**Version:** 0.1 · 2026-11-09 · Covers Phase 1 (foundation) and Phase 2 (attendance). Later phases are listed at the end.

| ID | Use case | Primary actor |
|---|---|---|
| UC-01 | Set up company, site and contract | Super Admin |
| UC-02 | Configure a site's attendance import profile | Super Admin |
| UC-03 | Import and clean the employee master | Super Admin / Processor |
| UC-04 | Upload a monthly attendance file | Processor |
| UC-05 | Review and resolve match exceptions | Processor |
| UC-06 | Handle a new (unmatched) employee | Processor |
| UC-07 | Propose and approve an employee exit | Processor → Approver |
| UC-08 | Generate and approve the attendance workbook | Processor → Approver |
| UC-09 | Ingest attendance from email | System |
| UC-10 | Request missing joiner details by email | System → Processor |
| UC-11 | View the monthly site dashboard | All MVP roles |
| UC-12 | Correct an employee record with audit | Processor → Approver |

---

### UC-02 Configure a site's attendance import profile
- **Actor:** Super Admin
- **Pre:** Site exists.
- **Main flow:** 1) Upload a sample file. 2) System shows sheets and columns. 3) Admin maps the ID, name, date/punch and status columns and sets the working-day rule. 4) System runs a test parse and shows the result. 5) Admin saves the profile as a new version.
- **Alt:** The sample doesn't parse → the system shows the failing row and reason.
- **Post:** Future files for this site use the profile.

### UC-03 Import and clean the employee master
- **Main flow:** 1) Upload the existing master Excel. 2) System maps columns and validates fields. 3) Shows possible duplicates (same name and DOB, same UAN, and so on) and missing mandatory fields. 4) User merges, fixes or accepts each one. 5) Approver signs off the baseline.
- **Post:** Each employee has a permanent internal ID; the original file is kept.

### UC-04 Upload a monthly attendance file
- **Main flow:** 1) Processor uploads the file. 2) System detects the site and month and the processor confirms. 3) System checks for a duplicate upload (hash). 4) Parses it with the site profile into standard rows. 5) Matches each row. 6) Shows a summary: matched / probable / ambiguous / unmatched / missing from file.
- **Alt:** Same file already processed → warn; reprocess only on explicit choice, as a new version.
- **Alt:** Parse fails → job marked Failed with the reason; original file kept.

### UC-05 Review and resolve match exceptions
- **Main flow:** For each exception the processor sees the incoming row next to candidate employees with matching evidence. They pick the right employee, create a provisional one, or reject the row. A confirmed name variant becomes an alias.
- **Rule:** Ambiguous rows are never assigned automatically.

### UC-06 Handle a new (unmatched) employee
- **Main flow:** 1) Processor creates a Provisional employee from the row. 2) The attendance is linked. 3) Missing mandatory fields are flagged. 4) (UC-10) A details request goes to the site. 5) Once complete, the approver activates the record.

### UC-07 Propose and approve an employee exit
- **Trigger:** An Active employee is missing from this month's file.
- **Main flow:** 1) System raises a "missing from attendance" exception, showing their recent attendance. 2) Processor marks them "Still active (absent)" or "Propose exit" with a date and reason. 3) Approver (a different user) approves or rejects. 4) On approval the status becomes Exited; history stays.
- **Rule:** No automatic exit, ever.

### UC-08 Generate and approve the attendance workbook
- **Pre:** No open High-priority exceptions for the site and month.
- **Main flow:** 1) Processor generates the workbook from the site template. 2) Previews it. 3) Submits for approval. 4) Approver approves; the file is versioned and locked.
- **Alt:** A change after approval → new revision with a reason; the old version is kept.

### UC-09 Ingest attendance from email
- **Main flow:** 1) System polls the mailbox (deivanayagam.k@sbgrps.com). 2) Matches the sender to a site. 3) Validates the attachment type. 4) Starts UC-04 automatically, with the processor confirming the month.
- **Alt:** Unknown sender or file → manual triage list.

### UC-10 Request missing joiner details by email
- **Main flow:** System drafts an email to the site sender listing provisional employees and the missing fields. Processor approves and sends. The reply is matched back to the pending request.

### UC-12 Correct an employee record with audit
- **Main flow:** Processor edits a field and gives a reason → the change is pending → the approver approves → the old and new values, user, time, reason and source are logged.

---

## Later-phase use cases (outline only)
- **Phase 3:** Ingest PF/ESI report · Match portal records by multiple fields · Review discrepancies side by side · Approve "replace master with portal value" · Send reconciliation summary email.
- **Phase 4:** Define a contract's document templates · Map fields · Generate billing documents · Approve and version.
- **Phase 5:** Site raises stock requisition · Vendor price confirmation · Approve quotation · Generate PO · Track delivery.
