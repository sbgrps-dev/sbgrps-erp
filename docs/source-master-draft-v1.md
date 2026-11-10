Dei 😂 understood. You want the complete business requirements and product vision, not another shortened overview.

We're documenting the actual ERP you're planning to build for SBGRPS, including every workflow, how information enters the system, how it gets processed, what happens when something goes wrong, what users need to approve, and what documents come out.

I'll retain all the details from the earlier breakdown, correct the site descriptions, include the future modules, and distinguish between the initial SBE implementation and the ultimate group-wide ERP.

# SBGRPS – Integrated Enterprise Resource Planning (ERP) System

PRODUCT VISION & BUSINESS REQUIREMENTS · MASTER DRAFT · V1.0

# SBGRPS ERP

One platform. Multiple companies. Multiple sites. One source of truth.

A centralised, semi-automated enterprise management platform designed to streamline workforce administration, attendance, statutory reconciliation, billing, procurement and operational documentation across Shree Balaji Groups.

# 4

Group business entities

# 12+

Known SBE site references, subject to validation

# 6

Initial development phases

# 1

Centralised data foundation

## 1. Organisation overview

SBGRPS stands for Shree Balaji Groups. It operates through multiple business entities, each with its own operational requirements, workforce, documentation and administrative processes.

The group consists of:

1. Shree Balaji Enterprises (SBE)
2. Shree Balaji Industries
3. Shree Karuppasamy Transports
4. PKR Automotive Limited

The ultimate objective is to develop an ERP capable of managing operations across all these entities.

However, the initial implementation will focus on Shree Balaji Enterprises, which manages multiple railway cleaning contracts across different stations and locations.

### 1.1 SBE operational sites

| Site code | Location / contract                 |
| --------- | ----------------------------------- |
| MSPFTR    | Platform and train-rake cleaning    |
| PTC       | Pass-through train cleaning, Egmore |
| JTJ       | Jolarpettai                         |
| KPD       | Katpadi                             |
| MAS       | Chennai Central                     |
| SRR       | Shoranur                            |
| MDU       | Madurai                             |
| TEN       | Tirunelveli                         |
| TN        | Tuticorin                           |
| RMM       | Rameswaram                          |
| TPJ Fort  | Tiruchirappalli Fort                |
| TBM       | Tambaram                            |
| GSN       | GSN operational site                |

Future onboarding: BBQ is currently on the waiting list. The system should support adding it when the contract becomes operational.

Each site has different employee counts, reporting procedures, biometric systems, attendance formats and document requirements.

This diversity is a major consideration in the system's architecture.

## 2. Product vision and objectives

The objective is to build a centralised ERP that reduces repetitive administrative work and establishes consistent data management across the organisation.

The current processes involve a substantial amount of manual work:

- Collecting attendance information from different sites.
- Processing different biometric exports.
- Matching employee names against master data.
- Updating monthly attendance records.
- Identifying employees who have joined or exited.
- Collecting missing employee information.
- Reconciling PF and ESI details.
- Correcting employee records across multiple documents.
- Generating monthly billing workbooks.
- Preparing statutory and contract-related documents.
- Preparing monthly stock requisitions.
- Communicating with vendors regarding product prices and orders.

The ERP should bring these workflows into one integrated platform.

### 2.1 Core philosophy: Semi-automation, not blind automation

The objective is not to remove human involvement from every process.

Instead, the system should automate repetitive data collection, processing, matching, validation, calculations and document preparation.

Human intervention should be reserved for:

- Approving important changes.
- Resolving ambiguous employee matches.
- Confirming employee exits.
- Reviewing statutory discrepancies.
- Approving billing documents.
- Approving purchase requisitions and orders.
- Handling exceptional situations.

The target is zero undetected errors and the highest achievable accuracy.

The system should never silently guess missing information or automatically apply an uncertain correction.

### 2.2 Fundamental design principle

One centralised source of truth, multiple operational workflows and reusable document-generation engines.

Employee information should be maintained centrally and reused across attendance, statutory reconciliation, billing and other modules.

Likewise, product, pricing and vendor information should be shared across procurement workflows.

## 3. System architecture and common processing workflow

The ERP should operate as a central processing platform between the different sources of operational information and the final business outputs.

Information can enter through Excel files, CSV files, biometric systems, emails, manual entries and future integrations.

Regardless of the source, the information should be converted into a standardised internal data structure before being used by other modules.

## End-to-end processing architecture

01\. Data collection

Excel · CSV · Biometric exports · Email · Manual entry · Integrations

02\. Data ingestion and standardisation

Read different formats and convert them into a common structure

03\. Central processing engine

Employee matching · Validation · Reconciliation · Calculations

04\. Exception detection and review

Missing records · Mismatches · Duplicate data · Approval queues

05\. Human verification and approval

Review · Correction · Approval · Rejection

06\. Final outputs

Excel workbooks · Reports · Billing documents · Emails · Purchase orders

### 3.1 Common processing requirements

Every module should follow consistent processing principles:

- Identify the source of the incoming information.
- Identify the associated company, site, contract and reporting period.
- Preserve the original uploaded file.
- Convert the data into standardised internal records.
- Validate mandatory fields and data types.
- Detect duplicate and conflicting records.
- Match records against the relevant master database.
- Maintain processing status and error information.
- Provide a review interface for unresolved cases.
- Generate outputs only after the required validations and approvals.

### 3.2 Excel-first architecture

Excel `.xlsx` is the primary operational input and output format.

The ERP must not force the organisation to immediately abandon its existing Excel-based processes.

Instead, it should:

- Import existing Excel files.
- Process different Excel structures.
- Preserve existing templates and layouts.
- Populate multiple workbooks from centralised data.
- Retain formulas, formatting, merged cells and other template-specific requirements wherever applicable.
- Generate downloadable workbooks.
- Support manual review and corrections before finalisation.

The internal database should remain the source of truth. Excel files are operational interfaces and generated documents, not the only place where business information exists.

# 4. Functional modules

## Module 01 – Organisation, Company, Site and Contract Management

Foundation module

Before implementing employee, attendance or billing workflows, the system needs a proper organisational hierarchy.

### 4.1 Organisational hierarchy

The ERP should support the following hierarchy:

SBGRPS – Group

Shree Balaji Enterprises

Shree Balaji Industries

Shree Karuppasamy Transports

PKR Automotive Limited

Sites and contracts

Individual operational locations and contract assignments

Departments, users and employees

### 4.2 Requirements

Each company should have its own:

- Company information and registration details.
- Employee records and associated workforce.
- Operational sites and contracts.
- Document templates.
- Billing configurations.
- Vendor associations.
- Authorised users and permissions.

A central group administrator should be able to oversee the entire organisation, while individual company administrators should have access only to their authorised business entities.

A site should be configurable with:

- Site code and name.
- Location.
- Associated company.
- Contract details.
- Contract commencement and expiry dates.
- Client details.
- Site-specific attendance source.
- Site-specific employee allocation.
- Required monthly documents.
- Associated vendors and products.
- Reporting and approval hierarchy.

The system must support new sites and contracts through configuration rather than requiring a new application for each location.

## Module 02 – Centralised Employee Master Data Management

Core foundation

The employee master database is arguably the most important component of the entire ERP.

All other employee-related modules should rely on this central database.

### 4.3 Employee master record

Every employee should have one central record with a unique internal employee ID.

Suggested information fields:

| Category          | Information                        |
| ----------------- | ---------------------------------- |
| Identification    | Employee ID, employee name, gender |
| Personal details  | DOB, parent name, Aadhaar          |
| Contact           | Mobile number, address             |
| Employment        | DOJ, designation, department       |
| Organisation      | Company, site, contract            |
| Banking           | Bank name, account number, IFSC    |
| PF                | UAN / PF number                    |
| ESI               | ESI number                         |
| Employment status | Active, exited, provisional        |
| Exit details      | Date of exit, reason, remarks      |

Additional fields should be configurable according to contractual and statutory requirements.

### 4.4 Single source of truth

The same employee information may be required in:

- Attendance sheets.
- Wage registers.
- Form XVII.
- Billing documents.
- PF and ESI records.
- Employee master workbooks.
- Monthly reconciliation reports.
- Other statutory and contract-specific documents.

Instead of maintaining independent copies of employee information, the ERP should retrieve it from the central database.

When an authorised correction is made, dependent working records and future document generations should use the updated information.

### 4.5 Employee lifecycle management

The system should maintain three primary employee categories:

A. Active employees

Employees currently working under the organisation or its contracts.

B. Exited employees

Employees who have left the organisation or whose employment has been formally terminated.

C. Provisional/new employees

Employees identified through attendance or other incoming records but whose information has not yet been fully collected or verified.

### 4.6 Employee exit workflow

When an employee appears in the master database but is missing from an attendance submission:

1. The system identifies the missing employee.
2. It checks previous attendance and available employment information.
3. It flags the employee for review.
4. The user confirms whether the employee has actually exited.
5. Once confirmed, the employee's status is changed to Exited.
6. The exit date and other relevant information are recorded.
7. The employee is moved into the exit register.
8. Historical attendance, billing and statutory records remain available.

An employee should never be deleted simply because their name is missing from one month's attendance sheet.

### 4.7 New employee onboarding workflow

When an incoming attendance file contains an employee who does not exist in the master database:

1. Identify the unmatched employee.
2. Create a provisional record.
3. Highlight the record for additional information.
4. Identify the originating site and attendance sender.
5. Prepare an automated email requesting the employee's details.
6. Allow information to be submitted through email or WhatsApp.
7. Extract the received details and populate the provisional record.
8. Verify the information.
9. Activate the employee record after approval.

Missing mandatory fields should remain visibly flagged until resolved.

### 4.8 Employee master data requirements

- Unique employee identification.
- Duplicate employee detection.
- Fuzzy name matching.
- Employee history.
- Employee-site allocation history.
- Document-level field mapping.
- Bulk import and export.
- Controlled master-data corrections.
- Full audit trail.
- Role-based access to sensitive personal information.

## Module 03 – Attendance Management and Reconciliation

Highest initial operational priority

### 4.9 Current problem

Attendance is one of the most time-consuming administrative activities.

Different sites use biometric systems, but the exported information is not standardised.

Some locations send biometric Excel/CSV exports, while other locations send manually prepared Excel sheets containing employee names and total working days.

The central office must manually interpret these files, identify employees, update monthly attendance records and prepare the required documents.

The objective is to make this a semi-automated process.

### 4.10 Supported attendance sources

| Source                       | Required processing                                |
| ---------------------------- | -------------------------------------------------- |
| Biometric Excel export       | Parse and standardise                              |
| Biometric CSV export         | Parse and standardise                              |
| Site attendance Excel        | Extract names and working days                     |
| Email attachment             | Automatically identify and process                 |
| Manual attendance entry      | Allow controlled entry and correction              |
| Future biometric integration | Direct or scheduled data retrieval where supported |

### 4.11 Biometric format standardisation

Every site may use a different biometric machine or export format.

The ERP should therefore include a configurable attendance import engine.

For each site, define an import configuration containing:

- File format.
- Sheet name.
- Employee identification column.
- Employee name column.
- Date and time columns.
- Punch-in and punch-out fields.
- Attendance status mapping.
- Shift or working-day calculation rules.
- Overtime fields, where applicable.
- Site-specific validation rules.

The incoming file should be transformed into a common attendance structure before further processing.

This avoids building entirely independent processing logic for each biometric machine.

### 4.12 Attendance processing workflow

1. Receive attendance file from site or biometric system.
2. Identify company, site and reporting month.
3. Read the file and map its columns.
4. Standardise attendance information.
5. Match employees against central master data.
6. Identify missing, duplicate, new or unmatched employees.
7. Populate the correct monthly attendance records.
8. Generate exceptions for human review.
9. Generate the final standardised Excel workbook after verification.

### 4.13 Attendance matching

For sites that submit only employee names and total working days, the system should:

- Match names against the employee master.
- Use employee IDs or unique identifiers where available.
- Use fuzzy matching as a fallback.
- Use other available identifying fields to resolve ambiguous matches.
- Avoid automatically assigning attendance when multiple employees have similar names.
- Populate the correct monthly attendance column.

Example:

| Employee     | Master status | Incoming attendance | Processing         |
| ------------ | ------------- | ------------------- | ------------------ |
| Ramesh Kumar | Active        | 28 days             | Matched            |
| Suresh M     | Active        | 26 days             | Matched            |
| Rajesh P     | Active        | Missing             | Flagged            |
| New employee | Not found     | 24 days             | Provisional record |

### 4.14 Attendance discrepancy handling

The system should identify:

- Employees in master data but absent from attendance.
- Employees in attendance but absent from master data.
- Duplicate employee entries.
- Duplicate attendance submissions.
- Invalid working-day counts.
- Missing dates.
- Conflicting attendance records.
- Unusual attendance patterns.
- Employee-site allocation conflicts.

Each discrepancy should have an identifiable status and resolution history.

### 4.15 Attendance output

The final output should be an `.xlsx` workbook following the existing attendance and reconciliation templates.

It must preserve:

- Existing column structures.
- Employee ordering where required.
- Existing formulas.
- Cell formatting.
- Monthly working-day columns.
- Required remarks.
- Site-specific document layouts.

The user should be able to preview, correct and approve the generated attendance before finalisation.

## Module 04 – PF and ESI Reconciliation Management

Critical statutory workflow

### 4.16 Current problem

Every month, an authorised person sends an email containing employee PF and ESI information obtained from the EPFO and ESIC portals.

The information must be compared against internal employee master data.

Employee names may not be identical between the internal records and portal records, making manual matching difficult.

The objective is to automate the comparison, identify discrepancies and prepare corrections for approval.

### 4.17 Incoming data collection

The system should:

1. Monitor the designated email source or accept manual uploads.
2. Identify incoming PF and ESI reports.
3. Extract employee details from attachments.
4. Identify the reporting period.
5. Standardise the extracted information.
6. Compare it against the central employee database.

The first version can process supplied portal exports. Direct portal scraping or API integration should be a separate capability, subject to portal permissions, technical availability and compliance requirements.

### 4.18 Intelligent employee matching

Matching should use multiple fields rather than relying exclusively on employee names.

| Field         | Matching purpose                                       |
| ------------- | ------------------------------------------------------ |
| Employee name | Fuzzy name matching                                    |
| DOB           | Identity verification                                  |
| DOJ           | Employment verification                                |
| Parent name   | Additional identity matching                           |
| Aadhaar       | Strong identity verification, where lawfully available |
| UAN           | PF account identification                              |
| ESI number    | ESI account identification                             |

The matching engine should assign confidence scores and distinguish between:

- High-confidence matches.
- Possible matches.
- Ambiguous matches.
- Unmatched records.

Sensitive identifiers should be masked in ordinary user interfaces, and matching should use appropriately protected data.

### 4.19 Discrepancy classification

The system should classify findings into the following categories:

| Status            | Meaning                                            |
| ----------------- | -------------------------------------------------- |
| ESI mismatch      | Internal ESI number differs from portal            |
| PF mismatch       | Internal PF/UAN differs from portal                |
| Both mismatched   | Both identifiers differ                            |
| ESI not in portal | Employee not found in ESI report                   |
| PF not in portal  | Employee not found in PF report                    |
| Both not found    | Employee missing from both datasets                |
| New employee      | Employee present internally but absent from portal |
| Uncertain match   | Identity cannot be confidently established         |

It should also distinguish a genuine identifier mismatch from an employee who has not yet been registered or whose portal record is unavailable in the reporting period.

### 4.20 Reconciliation review interface

The user should be able to view:

| Field         | Internal record | Portal record |
| ------------- | --------------- | ------------- |
| Employee name | Master name     | Portal name   |
| DOB           | Master DOB      | Portal DOB    |
| DOJ           | Master DOJ      | Portal DOJ    |
| Parent name   | Master value    | Portal value  |
| PF/UAN        | Internal number | Portal number |
| ESI           | Internal number | Portal number |

The interface should show the discrepancy type, matching confidence and recommended action.

### 4.21 Correction and replacement workflow

The user should be able to select individual employees or multiple employees and approve corrections.

For example, when the user chooses Replace master data with portal information:

1. The system records the existing internal value.
2. It displays the proposed replacement value.
3. The user reviews and approves the correction.
4. The central employee record is updated.
5. Relevant working master-data workbooks are synchronised.
6. Applicable document templates use the corrected information.
7. Existing records such as Form XVII are updated in the appropriate current or revised working version.
8. An explanatory remark is added.

Example remarks:

- `ESI mismatch (corrected in master data)`
- `PF mismatch (corrected in master data)`
- `PF and ESI mismatch (corrected in master data)`

All modifications must be traceable.

Previously submitted or officially filed documents must not be silently rewritten. Corrections to such records should follow the relevant revision and approval procedure.

### 4.22 Automated reconciliation email

Once processing and review are completed, the system should prepare an email containing:

- Total employees checked.
- PF discrepancies identified.
- ESI discrepancies identified.
- Both PF and ESI mismatches.
- Employees missing from the PF portal.
- Employees missing from the ESI portal.
- Newly joined employees.
- Employees requiring registration or activation.
- Unresolved discrepancies.
- Corrections approved and completed.

The email should be sent to the designated recipients after authorised review.

## Module 05 – Billing and Automated Document Generation

Major business value

### 4.23 Current problem

The organisation generates several billing and operational documents every month.

Most documents follow predefined Excel formats.

Although each document may have a different purpose and layout, a significant portion of the information is shared.

Currently, the same information is entered repeatedly into different files.

This leads to unnecessary work and inconsistencies.

### 4.24 Centralised document-generation engine

The proposed solution is to build one reusable engine that generates multiple documents from a shared set of verified data.

For example, a contract may require approximately 20 common fields.

Instead of filling out five or six different Excel documents separately, the user should enter the shared information once.

The system should map those fields to every applicable document template.

### 4.25 Illustrative common input fields

- Company name and details.
- Site name and location.
- Contract number.
- Work order number.
- Client details.
- Contractor details.
- Billing month.
- Billing period.
- Employee information.
- Employee count.
- Attendance information.
- Working days.
- Wage details.
- Applicable rates.
- Billing amounts.
- Statutory contribution details.
- Other contract-specific values.

The exact fields should be extracted from the existing templates, not assumed in advance.

### 4.26 Multi-document generation

For example, if a contract requires six documents:

One-time centralised data entry

# \~20 fields

Illustrative common fields

Billing document

Attendance statement

Form XVII

Wage register

Reconciliation sheet

Contract report

Simultaneous document generation

All templates populated from shared verified information

### 4.27 Detailed requirements

- Support multiple Excel templates per contract.
- Maintain individual template configurations.
- Map common fields to different cell locations.
- Support site-specific and contract-specific fields.
- Reuse employee and attendance data.
- Perform calculations using configurable rules.
- Validate all mandatory inputs.
- Identify inconsistencies between documents.
- Generate multiple workbooks in one operation.
- Preserve template formatting, formulas and layouts.
- Provide document previews.
- Allow manual corrections before final approval.
- Maintain generation history and document versions.
- Export final `.xlsx` files.

### 4.28 Contract-specific document configurations

Different contracts may have different document requirements.

The ERP should support a configurable template library.

For each contract, an administrator should be able to define:

- Required documents.
- Input fields.
- Field mappings.
- Calculation rules.
- Validation rules.
- Output naming conventions.
- Approval requirements.

This will allow new contracts to be onboarded without rebuilding the document-generation engine.

Expected outcome: Reduce hours of repeated document preparation to minutes of centralised data entry, verification and generation.

## Module 06 – Purchase Requisition and Purchase Order Management

Planned module

### 4.29 Current problem

Every month, individual sites send stock requirements for the upcoming month.

Currently, these requirements are manually prepared in Excel and communicated to the central office.

The administrative team then needs to check products, quantities, pricing, GST and vendor details before proceeding.

This entire process can be digitised.

### 4.30 Site-level stock requisition interface

Each authorised site representative should have access to a requisition interface.

The user should be able to:

1. Select the relevant site.
2. Select the upcoming requisition month.
3. Search for products.
4. Select the required product.
5. Enter the quantity.
6. Add remarks.
7. Submit the requisition.

The system should automatically retrieve product details from the central database.

### 4.31 Centralised product database

Every product should contain:

| Field        | Description                |
| ------------ | -------------------------- |
| Product ID   | Unique internal identifier |
| Product name | Display name               |
| Description  | Product specifications     |
| SKU          | Product code               |
| HSN          | HSN classification         |
| GST          | Applicable tax rate        |
| Base price   | Current reference price    |
| Unit         | Piece, litre, kg, etc.     |
| Vendor       | Associated supplier        |
| Vendor email | Registered contact         |
| Status       | Active/inactive            |

Pricing and GST information should be versioned so that historical requisitions remain accurate even when prices change.

### 4.32 Automatic price and GST calculation

When a site selects a product:

- Retrieve the current approved product price.
- Retrieve the applicable GST rate.
- Calculate the taxable amount.
- Calculate the applicable GST.
- Calculate the total.
- Display the complete cost breakdown.

Tax treatment should be based on the applicable transaction details and configured GST rules, rather than blindly applying a fixed tax calculation.

### 4.33 Vendor price confirmation

After the site submits its requisition:

1. The central office reviews the requested products and quantities.
2. The requisition is approved for vendor communication.
3. The system identifies the associated vendor.
4. It prepares a price-confirmation email.
5. The email includes product details, quantities, existing reference prices and GST details.
6. The vendor responds with confirmation or revised pricing.
7. The response is recorded against the requisition.
8. Price changes are flagged for approval.

### 4.34 Purchase order workflow

1. Site submits monthly stock requisition.
2. Central office reviews quantities and requirements.
3. System prepares vendor-specific price-confirmation email.
4. Vendor confirms or revises prices.
5. Authorised person approves the final quotation.
6. System generates the purchase order.
7. Order is tracked until delivery and fulfilment.

### 4.35 Additional procurement requirements

- Requisition status tracking.
- Approval hierarchy.
- Vendor master database.
- Product catalogue.
- Historical pricing.
- Vendor quotation history.
- Purchase order numbering.
- Partial order fulfilment.
- Delivery status.
- Pending order reports.
- Monthly site-wise procurement reports.
- Purchase history and audit trail.

## Module 07 – Vendor and Supplier Management

This module will provide the foundation for procurement and future financial workflows.

Each vendor record should contain:

- Vendor ID.
- Registered business name.
- Contact person.
- Email address.
- Mobile number.
- Registered address.
- GSTIN.
- PAN, where required.
- Bank details, where authorised.
- Products supplied.
- Approved pricing.
- Payment terms.
- Vendor status.
- Historical quotations.
- Purchase order history.

The vendor database should be shared with the procurement module.

A product may have one or more approved vendors, and the system should support vendor-specific pricing rather than assuming every product has one universal price.

## Module 08 – Inventory and Stock Management

This is a natural extension of the purchase requisition system.

Once procurement is established, the ERP can track the movement of materials across sites.

### Proposed functionality

- Central product catalogue.
- Site-wise stock records.
- Opening stock.
- Stock received.
- Stock issued.
- Stock consumed.
- Closing stock.
- Stock transfers between sites.
- Damaged or expired stock.
- Minimum stock thresholds.
- Reorder alerts.
- Monthly consumption reports.

The system should eventually connect purchase orders with goods receipt and inventory updates.

For example, when materials are delivered to a site, the authorised user records the received quantity. The system updates that site's stock balance.

## Module 09 – Payroll-supporting and Wage Management

This module should build on the employee master and attendance modules.

Its purpose is to centralise the employee-related information required for wage calculations and associated documentation.

### Proposed functionality

- Employee-wise attendance.
- Working-day calculations.
- Wage rates.
- Overtime calculations.
- Allowances and deductions.
- Applicable PF and ESI information.
- Monthly wage calculations.
- Site-wise wage summaries.
- Employee-wise wage statements.
- Wage registers.
- Reconciliation with attendance.

All calculations must follow approved company, contract and statutory rules.

The ERP should initially focus on preparing accurate payroll-supporting data and documents. Actual salary disbursement and statutory filing integrations can be added as separate capabilities.

## Module 10 – Statutory and Contract Document Management

This module should provide a common document repository and generation framework for statutory and contract-related documents.

### Proposed functionality

- Form XVII and applicable statutory registers.
- Employee master-data reports.
- Attendance registers.
- Wage registers.
- PF and ESI reconciliation reports.
- Contract-specific documents.
- Monthly document generation.
- Document revisions.
- Document approval.
- Historical document retrieval.

Each document should be linked to:

- Company.
- Site.
- Contract.
- Reporting month.
- Document type.
- Generation version.
- Approval status.

The system should distinguish between drafts, approved documents and documents already submitted or officially filed.

## Module 11 – Email and Communication Automation

This module will connect the ERP's operational workflows with the organisation's existing communication channels.

Email should be treated as an important data source, not merely a notification mechanism.

### 4.36 Incoming email processing

The ERP should support monitoring designated email inboxes for:

- Monthly attendance files.
- Biometric exports.
- PF and ESI reports.
- Employee information.
- Vendor quotations.
- Purchase confirmations.
- Other operational documents.

The system should identify relevant messages, classify attachments and route them to the appropriate module.

For example:

| Incoming email         | ERP action                          |
| ---------------------- | ----------------------------------- |
| JTJ monthly attendance | Route to attendance processing      |
| PF/ESI portal report   | Route to statutory reconciliation   |
| New employee details   | Match with pending employee request |
| Vendor quotation       | Attach to relevant requisition      |
| Purchase confirmation  | Update procurement workflow         |

The system should not process every attachment indiscriminately. It must validate the source, file type, reporting period and expected document structure.

### 4.37 Outgoing email automation

The system should prepare emails for:

- Missing employee information.
- Attendance discrepancies.
- PF/ESI reconciliation summaries.
- Employee portal registration or activation requests.
- Vendor price confirmations.
- Purchase orders.
- Monthly operational reports.

Emails should support:

- Configurable recipients.
- Reusable email templates.
- Dynamic employee, site and month information.
- Relevant Excel attachments.
- Draft and approval workflows.
- Sending history.
- Delivery and failure status, where available.

### 4.38 WhatsApp integration

WhatsApp should be considered an additional communication channel, especially for collecting missing employee information from site representatives.

Possible workflows:

- Request new employee details.
- Send reminders for pending information.
- Receive structured employee details.
- Notify users of pending approvals.
- Share selected operational reports.

The integration should use an approved WhatsApp Business API provider or supported integration. It should not depend on unofficial scraping or fragile browser automation for business-critical communication.

## Module 12 – Dashboard, Reporting and Exception Management

The ERP should have a central command centre that provides visibility into the status of all ongoing operations.

### 4.39 Main dashboard

The dashboard should display:

- Total companies.
- Active operational sites.
- Active employees.
- Newly joined employees awaiting information.
- Pending employee exits.
- Attendance files received.
- Attendance files pending processing.
- Attendance discrepancies.
- PF/ESI mismatches.
- Documents awaiting generation.
- Documents awaiting approval.
- Pending purchase requisitions.
- Vendor confirmations pending.
- Purchase orders awaiting fulfilment.

### 4.40 Centralised exception management

Rather than making users manually inspect every file, the system should maintain an exception queue.

Examples:

| Exception                              | Priority |
| -------------------------------------- | -------- |
| Employee not matched                   | High     |
| Duplicate employee                     | High     |
| PF/ESI mismatch                        | High     |
| Missing attendance                     | High     |
| Unusual working-day count              | High     |
| Missing mandatory employee information | Medium   |
| Vendor price changed                   | Medium   |
| Document generation warning            | Medium   |
| Pending vendor response                | Medium   |

Each exception should have:

- Reference ID.
- Associated company/site.
- Module.
- Description.
- Detected date.
- Assigned user.
- Priority.
- Resolution status.
- Resolution remarks.
- Audit history.

This makes the system exception-driven rather than requiring continuous manual inspection.

# 5. Cross-module requirements

These requirements apply to the entire ERP, not just individual modules.

| Requirement                | Expected behaviour                                  |
| -------------------------- | --------------------------------------------------- |
| Multi-company architecture | Support all SBGRPS entities                         |
| Multi-site architecture    | Site-level configuration and access                 |
| Centralised master data    | Shared employee, product and vendor records         |
| Role-based permissions     | Different access for different users                |
| Email integration          | Receive and send operational emails                 |
| WhatsApp integration       | Collect information and send notifications          |
| Excel processing           | Import and generate `.xlsx` workbooks               |
| Template engine            | Reuse existing business document templates          |
| Audit logs                 | Track every important modification                  |
| Version management         | Maintain historical document versions               |
| Exception management       | Centralise errors and unresolved cases              |
| Approval workflows         | Human verification for critical actions             |
| Backup and recovery        | Protect business-critical records                   |
| Reporting                  | Company, site and month-wise reports                |
| Notifications              | Alert users about pending work                      |
| Search                     | Search employees, sites, documents and transactions |

## 6. User roles and permissions

The ERP should support different user types according to their responsibilities.

| Role                     | Responsibilities                                |
| ------------------------ | ----------------------------------------------- |
| Group Super Admin        | Complete group-wide access                      |
| Company Admin            | Manage an assigned company                      |
| Central HR/Admin         | Employee records, attendance and reconciliation |
| Site Representative      | Submit attendance and stock requisitions        |
| Accounts/Billing User    | Prepare and review billing documents            |
| Procurement User         | Manage products, vendors and POs                |
| Reviewer                 | Verify processed records                        |
| Approver                 | Approve critical changes and documents          |
| Auditor / Read-only User | View permitted records and history              |

Permissions should be configurable.

For example, a site representative should not be able to change an employee's PF number or approve their own statutory corrections.

Sensitive employee and banking information should have restricted access.

# 7. Accuracy, validation and error prevention

This deserves its own section because reliability is one of the most important requirements of the ERP.

The system should be designed around the principle of zero undetected errors, rather than simply processing files quickly.

### 7.1 Validation at every stage

| Stage               | Validation                                        |
| ------------------- | ------------------------------------------------- |
| File upload         | File type, integrity, size and expected structure |
| Data extraction     | Missing fields and invalid values                 |
| Employee matching   | Identity confidence and duplicate detection       |
| Attendance          | Valid dates, working days and duplicate records   |
| PF/ESI              | Identifier comparison and identity verification   |
| Billing             | Required fields, calculations and consistency     |
| Procurement         | Product, price, GST and quantity validation       |
| Document generation | Template mapping and output integrity             |

### 7.2 No silent assumptions

The system must not:

- Automatically classify an absent employee as resigned.
- Assign attendance to an uncertain employee match.
- Replace PF/ESI numbers without approval.
- Accept an unverified vendor price change.
- Generate final documents with missing mandatory information.
- Overwrite previously approved or submitted records without a controlled revision.

### 7.3 Accuracy mechanisms

Recommended mechanisms include:

1. Unique employee IDs.
2. Confidence-based matching.
3. Duplicate detection.
4. Mandatory field validation.
5. Cross-document consistency checks.
6. Calculation verification.
7. Approval workflows.
8. Immutable audit events.
9. Original-file retention.
10. Reproducible document generation.

### 7.4 Audit trail

Every important change should record:

- Previous value.
- New value.
- Employee or record affected.
- User who made the change.
- Date and time.
- Reason for modification.
- Approval status.
- Associated source document.

This is especially important for employee exits, statutory corrections, attendance modifications and billing changes.

# 8. Document and data architecture

One of the most important technical decisions is to separate business data from document templates.

The ERP should not rely on individual Excel workbooks as independent databases.

Instead, it should maintain structured records and use those records to generate documents.

### 8.1 Centralised data entities

The initial data foundation should include:

| Data entity            | Purpose                              |
| ---------------------- | ------------------------------------ |
| Companies              | Group business entities              |
| Sites                  | Operational locations                |
| Contracts              | Contract-specific configuration      |
| Employees              | Central employee master              |
| Employee history       | Employment and allocation history    |
| Attendance             | Monthly and daily attendance records |
| Biometric mappings     | Site-specific import configurations  |
| PF/ESI records         | Statutory identifiers and history    |
| Reconciliation records | Comparison results and corrections   |
| Products               | Central product catalogue            |
| Vendors                | Supplier information                 |
| Pricing                | Vendor-specific price history        |
| Requisitions           | Site stock requirements              |
| Purchase orders        | Approved orders                      |
| Document templates     | Excel template definitions           |
| Generated documents    | Output files and versions            |
| Email records          | Incoming and outgoing communications |
| Audit logs             | Record of system actions             |

### 8.2 Document generation architecture

Every document should have:

- A template.
- A field-mapping configuration.
- A data source.
- Calculation rules.
- Validation rules.
- Output configuration.

For example, a billing document might retrieve:

- Company details from the company master.
- Site details from site configuration.
- Employee information from employee master.
- Attendance from attendance records.
- Wage calculations from the wage engine.
- Billing rates from contract configuration.

The document generator combines this information into the required Excel format.

### 8.3 Template reusability

A new contract should ideally require only:

1. Creating its contract configuration.
2. Adding its Excel templates.
3. Mapping the required fields.
4. Defining calculations.
5. Defining validation rules.
6. Testing the generated outputs.

This makes the platform scalable across different sites and contracts.

# 9. Development roadmap and implementation priorities

The development should be incremental, with each phase producing something operationally useful.

## Implementation roadmap

1. Phase 1 – ERP foundation

   First priority
   - Company and site management.
   - Contract management.
   - User roles and permissions.
   - Central employee master database.
   - Employee lifecycle management.
   - Excel import engine.
   - Initial data standardisation framework.
2. Phase 2 – Attendance management
   - Site-wise biometric configurations.
   - Different Excel/CSV import formats.
   - Attendance standardisation.
   - Employee matching.
   - Monthly attendance updates.
   - New employee detection.
   - Employee exit review.
   - Email attachment processing.
   - Attendance Excel generation.
3. Phase 3 – PF/ESI reconciliation
   - PF and ESI report ingestion.
   - Employee identity matching.
   - Discrepancy classification.
   - Review and correction interface.
   - Central master-data synchronisation.
   - Applicable document updates.
   - Reconciliation email generation.
4. Phase 4 – Billing and document automation
   - Centralised billing input.
   - Excel template library.
   - Common field mapping.
   - Contract-specific calculations.
   - Multiple document generation.
   - Document preview and approval.
   - Version history.
5. Phase 5 – Procurement and purchase orders
   - Product database.
   - Vendor database.
   - Site stock requisition interface.
   - GST and pricing calculations.
   - Vendor price confirmation emails.
   - Purchase order generation.
   - Order tracking.
6. Phase 6 – Group-wide expansion
   - Shree Balaji Industries.
   - Shree Karuppasamy Transports.
   - PKR Automotive Limited.
   - Additional contracts and sites.
   - Inventory management.
   - Expanded payroll workflows.
   - Advanced reporting.

### 9.1 Development priority within Phase 1 and Phase 2

I would prioritise actual operational value rather than developing every feature of a module before moving forward.

For example:

- First, establish the employee master.
- Next, import one site's attendance format.
- Validate the matching process against real data.
- Then introduce the next site's format.
- Once the processing engine is reliable, enable email ingestion.
- Finally, introduce the automated employee information collection workflow.

This allows us to test the system against actual operational files before expanding.

# 10. Non-functional requirements

These requirements determine how reliably the ERP operates as it grows.

| Area            | Requirement                                           |
| --------------- | ----------------------------------------------------- |
| Reliability     | No silent failures or unreported processing errors    |
| Accuracy        | Strict validation and human review of uncertain data  |
| Scalability     | Support additional companies, sites and employees     |
| Security        | Protect personal, financial and statutory information |
| Performance     | Process large Excel workbooks efficiently             |
| Availability    | Reliable access to central operational records        |
| Maintainability | Modular architecture and reusable processing engines  |
| Traceability    | Complete history of critical changes                  |
| Data integrity  | Prevent duplicate and conflicting records             |
| Backup          | Regular database and document backups                 |
| Recovery        | Restore operations after system failures              |

### 10.1 Data security

Employee records contain sensitive personal, banking and statutory information.

The ERP should implement:

- Role-based access control.
- Secure authentication.
- Encryption in transit and at rest.
- Masking of Aadhaar, bank account and statutory identifiers.
- Restricted document downloads.
- Audit logs for sensitive data access.
- Secure backup and recovery.
- Controlled retention and deletion policies.

### 10.2 Processing reliability

Every processing job should have a status, such as:

- Received.
- Queued.
- Processing.
- Completed.
- Completed with warnings.
- Failed.
- Awaiting review.
- Approved.

If processing fails, the original file should remain available and the system should clearly explain the reason.

Repeated uploads should not accidentally duplicate attendance or transactions. The system should identify previously processed files and support controlled reprocessing.

# 11. Success metrics and expected business impact

The ERP should be evaluated based on the time saved, accuracy achieved and reduction in administrative effort.

| Area                    | Success measure                                             |
| ----------------------- | ----------------------------------------------------------- |
| Employee management     | One reliable central employee record                        |
| Attendance              | Reduced manual matching and data entry                      |
| New employee onboarding | Faster collection of missing details                        |
| Employee exits          | Reliable lifecycle and historical records                   |
| PF/ESI                  | Faster discrepancy identification                           |
| Billing                 | Multiple documents generated from shared inputs             |
| Procurement             | Digital requisitions replacing repetitive Excel preparation |
| Communication           | Reduced manual follow-ups                                   |
| Document management     | Consistent and traceable outputs                            |
| Expansion               | New sites onboarded through configuration                   |

### The primary operational target

Consider a process that currently takes several hours because an administrator must open multiple Excel files, copy employee information, match names, update values and prepare several documents.

The intended workflow should be:

1. Upload or receive the required files.
2. Allow the ERP to process and reconcile information.
3. Review flagged exceptions.
4. Approve the results.
5. Generate all required documents.

The human effort should shift from repetitive data entry to reviewing and making decisions.

The ultimate measure of success is how much administrative work can be eliminated without compromising accuracy, compliance or operational control.

# 12. Future expansion opportunities

These are not necessarily part of the initial release, but the ERP architecture should leave room for them.

| Future capability      | Potential functionality                                   |
| ---------------------- | --------------------------------------------------------- |
| Advanced payroll       | End-to-end wage and payroll processing                    |
| Inventory              | Site-wise material and stock tracking                     |
| Vendor management      | Supplier performance and pricing history                  |
| Financial management   | Expense, payable and receivable workflows                 |
| Contract management    | Contract lifecycle and renewal tracking                   |
| Asset management       | Equipment and asset allocation                            |
| Management reporting   | Group-wide business analytics                             |
| Employee self-service  | Employee information and document access                  |
| Mobile application     | Site-level operations and approvals                       |
| Biometric integration  | Direct attendance data collection                         |
| Statutory integrations | Supported portal/API integrations                         |
| AI-assisted processing | Document classification, extraction and anomaly detection |

These should be introduced only when the corresponding business requirements are established.

# 13. Product principles – Non-negotiable

I would put these principles at the end of the PRD because they will guide every future development decision.

1\. Centralisation: One source of truth for all business-critical information.

2\. Semi-automation: Automate repetitive work, retain human control over important decisions.

3\. Accuracy first: Never sacrifice correctness for processing speed.

4\. Excel compatibility: Respect existing operational document formats.

5\. Reusability: Build one configurable engine rather than separate hardcoded solutions for every site.

6\. Exception-driven processing: Automatically handle valid records and bring only problematic records to the user's attention.

7\. Complete traceability: Every critical modification must be accountable.

8\. Modular expansion: New business entities, sites and workflows should integrate without rebuilding the ERP.

9\. Operational continuity: The ERP must improve existing processes without unnecessarily disrupting day-to-day operations.

10\. Human accountability: Final responsibility for critical business decisions remains with authorised personnel.

# 14. Final product definition

# SBGRPS ERP

Product vision

An integrated, centralised and semi-automated enterprise management platform for Shree Balaji Groups.

Designed to unify workforce administration, attendance processing, statutory reconciliation, billing, procurement, vendor management and operational documentation across multiple companies, sites and contracts.

The platform will use centralised master data, configurable processing engines, reusable document templates and human-in-the-loop approval workflows to minimise repetitive administrative work and maximise data accuracy.

Initial implementation

Shree Balaji Enterprises – employee master, attendance, PF/ESI reconciliation and billing automation.

Ultimate objective

A unified ERP serving all four SBGRPS business entities and their operational requirements.

## 15. My recommendations before we start actual development

There are five things I would establish before writing the technical implementation PRD.

1\. Collect existing Excel files: Gather actual attendance formats from every active site, existing employee master sheets, PF/ESI reports and every monthly billing template.

2\. Map the existing workflows: Document exactly who sends each file, who processes it, who approves it and where the final document goes.

3\. Establish the master data: Reconcile existing employee records and identify duplicate, incomplete and outdated information before treating the new database as authoritative.

4\. Build the processing engine first: The reusable Excel ingestion, standardisation, matching, validation and document-generation infrastructure is more valuable than developing isolated automation scripts.

5\. Test against historical months: Run the ERP against already processed attendance and billing records, compare the outputs against approved originals, and resolve discrepancies before relying on it operationally.

### One important distinction

This document is the business/product requirements foundation. The next technical PRD should translate it into:

- Detailed functional requirements and acceptance criteria.
- Database schema and entity relationships.
- Module architecture and dependencies.
- API specifications.
- Excel import/export specifications.
- Email and WhatsApp integration specifications.
- Approval and permission matrices.
- Error handling and audit requirements.
- UI/UX screens and user journeys.
- Testing and deployment strategy.

My strongest recommendation: Do not start by building 12 modules independently. Build the common foundation that all 12 modules depend on. That is what will make this a proper ERP rather than a collection of automation tools.
note multi ducmment that 20 average fields is not for now, it is is bbq,gsn and TBM sites if we acquired if not we dont hav e that in dev plan go through and ask iof any douibts