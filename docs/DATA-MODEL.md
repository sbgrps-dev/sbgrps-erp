# SBGRPS ERP — MVP data model

**Version:** 0.1 · 2026-11-09 · Postgres-first. All tables have `id`, `created_at`, `updated_at`, `created_by`, `updated_by`.

> Table names in `snake_case`. Soft deletes via `deleted_at` only where listed; everything else is hard-kept. Every change on a critical table is mirrored into `audit_log`.

## 1. Organisation

```
company
  id, code, name, registration_details JSONB

site
  id, company_id → company, code UNIQUE, name, location, status ENUM(live, waiting_list, closed)

contract
  id, site_id → site, contract_no, client, start_date, end_date,
  rate_card JSONB,          -- { "standard_day": 505, "car_wash_day": 525, "ot_day": 200 }
  manpower_rules JSONB      -- { "pftr": {factor: 0.23, base: 2066}, "cts": {factor: 0.2, base: 4405}, "sup_per_day": 3, "watering_base": 7492 }

import_profile
  id, site_id → site, version, file_type, sheet_rules JSONB, column_map JSONB,
  working_day_rule JSONB, is_active BOOL
```

## 2. People

```
person                                  -- the human being
  id, display_name, dob, gender, father_or_husband_name,
  aadhaar_encrypted BYTEA,              -- AES-encrypted, masked in UI
  mobile, address

employment                              -- one spell at one contract (rejoin = new row)
  id, person_id → person, employee_code,  -- e.g. 101, 155; unique within (site, contract, spell)
  site_id → site, contract_id → contract,
  designation, status ENUM(provisional, active, exited),
  date_of_joining, date_of_exit, exit_reason,
  pf_uan, esi_no,
  bank_account_encrypted BYTEA, ifsc, bank_branch,
  alternate_account_name,
  wages_per_day NUMERIC, remarks TEXT

employee_alias                           -- learned name variants for matching
  id, person_id → person, alias_name, source_site_id, added_by_user, confirmed_at
```

> Rejoiner model: one `person` can have many `employment` rows. Each employment keeps its own ID and history. This is non-destructive and matches the "LEFT SITE" section of today's master.

## 3. Users and access

```
app_user
  id, email, name, status, password_hash, last_login_at

role
  id, code ENUM(super_admin, processor, approver, auditor, site_rep)

user_role                                 -- optional company/site scoping
  user_id, role_id, company_id?, site_id?
```

## 4. Attendance

```
source_file
  id, site_id, month DATE, received_at, received_via ENUM(upload, email),
  original_name, sha256, bytes_url, uploaded_by

import_job
  id, source_file_id, import_profile_id, status ENUM(received, processing, awaiting_review, approved, failed),
  error_reason TEXT, started_at, finished_at, version INT

attendance_row                              -- one row per employment per shift per day
  id, import_job_id, employment_id,
  shift SMALLINT CHECK (shift IN (1,2,3)),
  day SMALLINT CHECK (day BETWEEN 1 AND 31),
  trip SMALLINT,                            -- for shift 3 watering (1-3), NULL otherwise
  state ENUM(present, present_dummy, absent),
  match_confidence ENUM(exact, probable, ambiguous, unmatched),
  source_row_ref JSONB,                     -- sheet + row + col for traceability
  origin ENUM(railway_biometric, topup_rejoin, topup_new, topup_car_wash, topup_missed, topup_watering, topup_other)

exception
  id, import_job_id, type ENUM(unmatched, ambiguous, missing_from_file, duplicate, invalid_day_count, partial_biometric),
  priority ENUM(high, medium, low), status ENUM(open, resolved, rejected),
  assignee_user_id, resolution_note, resolved_at, employment_id?, source_row_ref JSONB
```

## 5. Payroll summary (per month, generated from attendance_row)

```
payroll_summary
  id, site_id, month DATE, employment_id,
  shift1_days, shift2_days, shift3_days,
  total_wrk_days, dummy_days, total_days, ot_days, actual_days,
  salary NUMERIC,
  rate_type ENUM(standard, car_wash, override),
  manual_salary NUMERIC,             -- non-null when overridden (night shift, supervisor, etc.)
  remarks TEXT,
  approved_at, approved_by

UNIQUE (site_id, month, employment_id)
```

## 6. Output and approvals

```
generated_document
  id, site_id, month, document_type ENUM(sbe_attendance_workbook, …future…),
  version INT, status ENUM(draft, approved, submitted),
  template_ref, output_bytes_url, generated_by, approved_by, approved_at
UNIQUE (site_id, month, document_type, version)

approval_request
  id, action ENUM(exit, master_correction, workbook),
  subject_id BIGINT, subject_table TEXT,
  requested_by, requested_at, status ENUM(pending, approved, rejected),
  reviewer_id, reviewed_at, reason TEXT
```

## 7. Audit (every critical change)

```
audit_log
  id, entity_table, entity_id, field, old_value JSONB, new_value JSONB,
  user_id, happened_at, reason, source_file_id?
```

## 8. Later-phase placeholders (empty in MVP)

- `pf_esi_portal_record`, `reconciliation_item` — Phase 3.
- `document_template`, `template_field_map` — Phase 4 billing/annexures.
- `product`, `vendor`, `vendor_price`, `requisition`, `purchase_order` — Phase 5.
- `communication_rule`, `incoming_email`, `outbound_email` — Phase 2 end / Phase 3.

## 9. Design notes

- **PII at rest:** `aadhaar_encrypted` and `bank_account_encrypted` are encrypted with a per-column key, decrypted only at view time, and every decryption is written to `audit_log`.
- **Site-scoped queries:** every non-admin query is filtered by the user's `user_role.site_id` or `company_id`. Enforced in a row-level policy, not just the app layer.
- **Why `employment` and not `employee_site_allocation`:** the real master already models employment as a separate line per spell. Keeping that shape avoids data loss on migration.
- **Why `attendance_row` is one row per (employment, shift, day, trip):** we can rebuild any annexure, the payroll summary, and any later statutory doc off this single table without re-parsing files.
