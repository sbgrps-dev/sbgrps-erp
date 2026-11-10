# SBGRPS ERP — UML diagrams (MVP)

**Version:** 0.1 · 2026-11-09 · Mermaid diagrams. They render on GitHub, in VS Code (Markdown Preview Mermaid extension) and at https://mermaid.live. Field lists will firm up after the sample files are reviewed.

## 1. Use-case diagram

```mermaid
flowchart LR
    SA([Super Admin])
    PR([Attendance Processor])
    AP([Approver])
    MAIL([Mailbox / System])

    subgraph ERP["SBGRPS ERP — MVP"]
        UC1[UC-01 Set up company / site / contract]
        UC2[UC-02 Configure import profile]
        UC3[UC-03 Import & clean employee master]
        UC4[UC-04 Upload attendance file]
        UC5[UC-05 Resolve match exceptions]
        UC6[UC-06 Handle new employee]
        UC7[UC-07 Propose / approve exit]
        UC8[UC-08 Generate & approve workbook]
        UC9[UC-09 Ingest attendance from email]
        UC10[UC-10 Request joiner details]
        UC11[UC-11 View dashboard]
        UC12[UC-12 Correct employee record]
    end

    SA --> UC1 & UC2 & UC3
    PR --> UC3 & UC4 & UC5 & UC6 & UC7 & UC8 & UC11 & UC12
    AP --> UC7 & UC8 & UC12 & UC11
    MAIL --> UC9 & UC10
    UC9 -. includes .-> UC4
    UC4 -. includes .-> UC5
    UC5 -. extends .-> UC6
    UC6 -. extends .-> UC10
```

## 2. Class diagram (core domain)

Enums: Site.status = Live / WaitingList / Closed · Employee.status = Provisional / Active / Exited · ImportJob.status = Received / Processing / AwaitingReview / Approved / Failed · AttendanceRecord.match_confidence = Exact / Probable / Ambiguous / Unmatched · GeneratedDocument.status = Draft / Approved / Submitted. Bank and ID numbers are stored encrypted.

```mermaid
classDiagram
    class Company {
        +id
        +name
        +code
        +registration_details
    }
    class Site {
        +id
        +code
        +name
        +location
        +status
    }
    class Contract {
        +id
        +contract_no
        +client
        +start_date
        +end_date
    }
    class Employee {
        +id
        +name
        +gender
        +dob
        +parent_name
        +mobile
        +doj
        +designation
        +uan_pf
        +esi_no
        +bank_account
        +status
        +exit_date
        +exit_reason
    }
    class EmployeeAlias {
        +alias_name
        +source_site
        +biometric_id
    }
    class SiteAllocation {
        +from_date
        +to_date
    }
    class ImportProfile {
        +version
        +file_type
        +sheet_name
        +column_map
        +working_day_rule
    }
    class SourceFile {
        +id
        +file_hash
        +original_name
        +received_via
        +period_month
    }
    class ImportJob {
        +status
        +error_reason
        +version
    }
    class AttendanceRecord {
        +period_month
        +days_present
        +daily_detail
        +match_confidence
        +source_row
    }
    class ExceptionItem {
        +type
        +priority
        +status
        +assignee
        +resolution_note
    }
    class Approval {
        +action
        +requested_by
        +approved_by
        +status
        +reason
    }
    class GeneratedDocument {
        +template_name
        +version
        +status
        +file_path
    }
    class AuditLog {
        +entity
        +field
        +old_value
        +new_value
        +user
        +timestamp
        +reason
    }
    class User {
        +email
        +role
    }

    Company "1" --> "*" Site
    Site "1" --> "*" Contract
    Site "1" --> "*" ImportProfile
    Employee "1" --> "*" SiteAllocation
    Site "1" --> "*" SiteAllocation
    Employee "1" --> "*" EmployeeAlias
    SourceFile "1" --> "*" ImportJob
    ImportJob --> ImportProfile : uses
    ImportJob "1" --> "*" AttendanceRecord
    AttendanceRecord "*" --> "0..1" Employee
    ImportJob "1" --> "*" ExceptionItem
    ExceptionItem --> Approval : may need
    Site "1" --> "*" GeneratedDocument
    User "1" --> "*" AuditLog
```

## 3. Sequence: monthly attendance processing (MSPFTR)

```mermaid
sequenceDiagram
    actor P as Processor
    participant UI as Web app
    participant API as Backend
    participant ENG as Import engine
    participant DB as Database
    actor A as Approver

    P->>UI: Upload MSPFTR biometric file
    UI->>API: POST /imports (file, site, month)
    API->>DB: Store original file + hash
    alt Same hash already processed
        API-->>UI: Warn "already processed"
    else New file
        API->>ENG: Parse with MSPFTR import profile
        ENG->>ENG: Standardise rows
        ENG->>DB: Look up employees by ID / alias / fuzzy name
        ENG->>DB: Save attendance rows + confidence
        ENG->>DB: Create exceptions (unmatched, ambiguous, missing, duplicates)
        API-->>UI: Summary + exception list
    end
    loop Each exception
        P->>UI: Link to employee / create provisional / propose exit
        UI->>API: Resolve
        API->>DB: Update + audit log
    end
    P->>UI: Generate workbook
    API->>DB: Fill site template
    API-->>UI: Preview
    P->>UI: Submit for approval
    A->>UI: Review changes + preview
    A->>UI: Approve
    API->>DB: Lock version, record approval
```

## 4. State diagram: employee lifecycle

```mermaid
stateDiagram-v2
    [*] --> Provisional : Unmatched in attendance
    [*] --> Active : Imported from clean master
    Provisional --> Active : Details complete + approved
    Provisional --> Rejected : Not a real employee / duplicate
    Active --> ExitProposed : Missing from attendance → processor proposes
    ExitProposed --> Active : Approver rejects / still employed
    ExitProposed --> Exited : Approver confirms
    Exited --> Active : Rejoins (approved)
    Exited --> [*]
```

## 5. Activity: matching an incoming attendance row

```mermaid
flowchart TD
    R[Incoming row] --> ID{Has employee or biometric ID?}
    ID -- Yes --> IDM{ID found in master / aliases?}
    IDM -- Yes --> EX[Exact match → apply]
    IDM -- No --> NM
    ID -- No --> NM{Name / alias match within site}
    NM -- One exact alias --> EX
    NM -- One fuzzy candidate --> PB[Probable → review]
    NM -- Several candidates --> AM[Ambiguous → review]
    NM -- None --> UN[Unmatched → provisional employee?]
    PB --> H[Human decides]
    AM --> H
    UN --> H
    H --> AL[Save alias for next month]
```
