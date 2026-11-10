# SBGRPS ERP — Stocks module UML

**Version:** v0.3 · 2026-11-10 · Mermaid. Open in VS Code, GitHub or https://mermaid.live.

## 0. Where this fits

Single-user v0 — pre-release (prem does everything). Output is the September 2026 two-sheet layout: `Product Details` + `Vendor Details`. No Uniform sheet, no current-stock column. Save never sends. Two separate send flows: one to HQ (requisition Excel), one to vendors (price verification sheet). See [PRD-STOCKS.md](PRD-STOCKS.md).

## 1. Use-case diagram

```mermaid
flowchart LR
    OP([prem — Operator])
    MAIL([Email system])
    VEN([Vendor — external])

    HQ([HQ — vidyaparam@sbgrs.com])
    subgraph Stocks["Stocks module — v0"]
        U1[UC-S1 Manage vendors]
        U2[UC-S2 Manage products & prices]
        U3[UC-S3 Open month / site requisition]
        U4[UC-S4 Add product line, enter qty]
        U5[UC-S5 Generate Excel in September template]
        U6[UC-S6 Review and edit]
        U7[UC-S7 Save requisition]
        U8[UC-S8 Send requisition to HQ]
        U8m[UC-S8m Mark as sent manually]
        U9[UC-S9 Send price list to vendors]
        U10[UC-S10 Capture vendor price reply, accept / reject]
        U11[UC-S11 View history]
    end

    OP --> U1 & U2 & U3 & U4 & U5 & U6 & U7 & U8 & U8m & U9 & U10 & U11
    MAIL --> U8 & U9 & U10
    HQ --> U8
    VEN --> U10
    U4 -. feeds .-> U5
    U5 -. feeds .-> U6
    U6 -. ok .-> U7
    U7 -. optional .-> U8
```

## 2. Class diagram

```mermaid
classDiagram
    class Site {
        +id
        +code  "MSPFTR_PT, MS_OFFICE, TPJ_BIO, ..."
        +display_name  "MS PFTR & PT, MS OFFICE, ..."
        +status
    }
    class Vendor {
        +id
        +name
        +gstin
        +address
        +phones
        +emails
        +website
        +drug_licence
        +status
    }
    class Product {
        +id
        +code
        +name
        +aliases  "list"
        +description
        +unit  "Litres, Nos, Kg, Set, ..."
        +hsn
        +gst_rate
        +status
    }
    class ProductVendor {
        +is_preferred
    }
    class ProductPrice {
        +price
        +effective_from
        +effective_to
        +source  "office_edit | vendor_reply"
        +reason
    }
    class StockRequisition {
        +id
        +month
        +status  "Draft | Saved | SentToHQ | SentManually | Closed"
        +total_taxable
        +total_gst
        +total_amount
        +created_by
        +updated_at
    }
    class RequisitionLine {
        +id
        +sno
        +qty_required
        +unit_snapshot
        +price_snapshot
        +gst_rate_snapshot
        +taxable_amount
        +gst_amount
        +line_total
        +notes
    }
    class GeneratedWorkbook {
        +id
        +version
        +file_url
        +generated_at
    }
    class HqEmail {
        +id
        +status  "Draft | Sent | Failed"
        +recipient  "vidyaparam@sbgrs.com"
        +subject
        +body
        +attachment_url
        +sent_at
        +message_id
    }
    class PriceListEmail {
        +id
        +status  "Draft | Sent | Failed | ReplyReceived"
        +vendor_id
        +subject
        +body
        +attachment_url  "SNO | Product Name | Price | GST | HSN"
        +sent_at
        +message_id
    }
    class PriceListReply {
        +id
        +received_at
        +body
        +raw_attachment_url
    }
    class PriceListReplyLine {
        +id
        +product_id
        +current_price
        +proposed_price
        +status  "Pending | Accepted | Rejected"
        +decided_at
    }
    class AuditLog {
        +entity
        +field
        +old_value
        +new_value
        +user
        +at
        +reason
    }

    Vendor "1" --> "*" ProductVendor
    Product "1" --> "*" ProductVendor
    ProductVendor "1" --> "*" ProductPrice
    Site "1" --> "*" StockRequisition
    StockRequisition "1" --> "*" RequisitionLine
    RequisitionLine "*" --> "1" Product
    RequisitionLine "*" --> "1" Vendor
    StockRequisition "1" --> "*" GeneratedWorkbook
    StockRequisition "1" --> "*" HqEmail
    Vendor "1" --> "*" PriceListEmail
    PriceListEmail "1" --> "*" PriceListReply
    PriceListReply "1" --> "*" PriceListReplyLine
    PriceListReplyLine "*" --> "1" Product
```

> No `ProductVariant`, no `SiteProduct`, no `opening_stock`. prem ruled out uniform size breakdowns, per-site catalogues and current-stock entry for the MVP.

## 3. Sequence A: monthly requisition → Save → Send to HQ

```mermaid
sequenceDiagram
    actor OP as prem
    actor HQ as HQ (vidyaparam)
    participant UI as Web UI
    participant API as Backend
    participant DB as Database
    participant GEN as Excel generator
    participant MAIL as Email

    OP->>UI: Open month → pick site (e.g. MS PFTR & PT)
    UI->>API: GET requisition(site, month)
    alt First time this month
        API->>DB: Create empty Draft
    end
    API-->>UI: Draft
    OP->>UI: Search product ("sterix")
    OP->>UI: Pick product, enter qty, optional vendor switch
    UI->>API: Add line
    API->>DB: Snapshot unit / price / gst_rate, compute totals
    OP->>UI: Generate Excel
    API->>GEN: Build two-sheet workbook (Product Details, Vendor Details)
    GEN-->>API: file.xlsx
    API->>DB: Store GeneratedWorkbook v1
    API-->>UI: Review pane
    alt Needs edits
        OP->>UI: Edit a line → Regenerate → v2
    end
    OP->>UI: Save
    DB-->>UI: Requisition status = Saved
    note over OP,UI: No email is sent. prem decides when to send.
    alt Send through the app
        OP->>UI: Send to HQ
        API->>DB: Draft HqEmail for vidyaparam@sbgrs.com with full Excel
        OP->>UI: Review & Send
        UI->>MAIL: Send
        MAIL-->>HQ: Requisition email + Excel
        DB-->>UI: status = SentToHQ
    else Send manually from Gmail
        OP->>UI: Mark as sent manually (date)
        DB-->>UI: status = SentManually
    end
    HQ->>HQ: Reviews, issues PO (outside the app)
```

## 3b. Sequence B: price verification to vendors

```mermaid
sequenceDiagram
    actor OP as prem
    actor V as Vendor
    participant UI as Web UI
    participant API as Backend
    participant DB as Database
    participant MAIL as Email

    OP->>UI: Open Price Verification
    UI->>API: List vendors + their products + current prices
    OP->>UI: Pick vendor(s) + which products
    OP->>UI: Send price list
    API->>DB: Draft PriceListEmail per vendor, attachment: SNO, Product, Price, GST, HSN
    OP->>UI: Review & Send
    UI->>MAIL: Send
    MAIL-->>V: Price verification email + Excel
    V-->>MAIL: Reply with confirmed / revised prices
    MAIL-->>API: Inbound thread captured
    API->>DB: Attach PriceListReply + parse hints into PriceListReplyLine (pending)
    OP->>UI: Review each line (current vs proposed)
    OP->>UI: Accept / Reject per line
    alt Accepted
        API->>DB: New ProductPrice row (source = vendor_reply)
    else Rejected
        API->>DB: Mark line Rejected, prices unchanged
    end
```

## 4. State diagram: StockRequisition

```mermaid
stateDiagram-v2
    [*] --> Draft : month / site opened
    Draft --> Draft : add / edit / remove line (regenerate)
    Draft --> Saved : prem clicks Save
    Saved --> Draft : prem reopens to edit
    Saved --> SentToHQ : prem clicks Send to HQ, email sent
    Saved --> SentManually : prem marks sent manually
    SentToHQ --> Closed : month wrapped up
    SentManually --> Closed : month wrapped up
    Closed --> [*]
```

## 5. Activity: adding a line

```mermaid
flowchart TD
    S[prem searches for product] --> M{Alias / name match?}
    M -- Yes --> P[Pick product]
    M -- No --> N[Create product inline]
    N --> V1{Assign at least one vendor}
    V1 --> P
    P --> V2{Product has one approved vendor?}
    V2 -- Yes --> A[Use that vendor, snapshot price]
    V2 -- No --> C[prem picks vendor]
    C --> A
    A --> Q[Enter qty]
    Q --> T[Compute taxable, GST, total from snapshot]
    T --> L[Line added]
```

## 6. Data flow (context)

```mermaid
flowchart LR
    CAT[(Master product + price catalogue)] --> ERP
    VDIR[(Vendor directory)] --> ERP
    OP[prem's qty entries] --> ERP
    ERP --> XLSX[Excel: Product Details + Vendor Details<br/>September layout]
    XLSX --> HQMAIL[Email to HQ<br/>vidyaparam@sbgrs.com]
    HQMAIL --> HQ[HQ issues PO<br/>outside the app]
    ERP --> PVXLSX[Price verification sheet<br/>SNO, Product, Price, GST, HSN]
    PVXLSX --> VMAIL[Email per vendor]
    VMAIL --> VREP[(Vendor price replies)]
    VREP --> ERP
    ERP --> HIST[(Monthly requisition history<br/>+ HQ email log<br/>+ price-list emails)]
```
