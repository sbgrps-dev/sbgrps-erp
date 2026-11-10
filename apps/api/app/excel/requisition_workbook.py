"""Builds the two-sheet stock requisition workbook in the September 2026 layout.

Sheet 1 `Product Details`, sheet 2 `Vendor Details`. No `Uniform Details` sheet.
"""

from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.excel import styles as st
from app.schemas.preview import Preview, VendorDetail

PRODUCT_HEADERS = [
    "SNO",
    "SITE",
    "MONTH",
    "VENDOR NAME",
    "CHEMICAL / MATERIAL NAME",
    "QTY REQ.",
    "UNIT",
    "PER COST",
    "TAXABLE AMOUNT",
    "GST",
    "GST AMOUNT",
    "TOTAL",
]
PRODUCT_WIDTHS = [6, 16, 9, 26, 36, 10, 9, 11, 16, 7, 13, 14]
LAST_COL = len(PRODUCT_HEADERS)


def _qty_value(qty: Decimal) -> tuple[Decimal | int, str]:
    if qty == qty.to_integral_value():
        return int(qty), st.INT_FMT
    return qty.normalize(), st.QTY_FMT


def _box(ws: Worksheet, row: int) -> None:
    for col in range(1, LAST_COL + 1):
        ws.cell(row=row, column=col).border = st.BORDER


def _merge_down(ws: Worksheet, col: int, first: int, last: int) -> None:
    if last > first:
        ws.merge_cells(start_row=first, start_column=col, end_row=last, end_column=col)


def _total_row(ws: Worksheet, row: int, label: str, taxable, gst, total, fill) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    label_cell = ws.cell(row=row, column=1, value=label)
    label_cell.font = st.BOLD
    label_cell.alignment = st.RIGHT
    for col, value in ((9, taxable), (11, gst), (12, total)):
        c = ws.cell(row=row, column=col, value=value)
        c.number_format = st.MONEY_FMT
        c.font = st.BOLD
    for col in range(1, LAST_COL + 1):
        ws.cell(row=row, column=col).fill = fill
    _box(ws, row)


def _product_sheet(ws: Worksheet, preview: Preview) -> None:
    ws.title = "Product Details"
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=LAST_COL)
    title = ws.cell(row=1, column=1, value=preview.title)
    title.font = st.TITLE_FONT
    title.alignment = st.CENTER
    ws.row_dimensions[1].height = 24

    for col, header in enumerate(PRODUCT_HEADERS, start=1):
        c = ws.cell(row=2, column=col, value=header)
        c.font = st.HEADER_FONT
        c.fill = st.HEADER_FILL
        c.alignment = st.CENTER
        c.border = st.BORDER
    ws.row_dimensions[2].height = 30
    for col, width in enumerate(PRODUCT_WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "A3"

    row = 3
    for site in preview.sites:
        site_first = row
        for vendor in site.vendors:
            vendor_first = row
            for line in vendor.lines:
                qty, qty_fmt = _qty_value(line.qty)
                values = [
                    (line.sno, st.INT_FMT, st.CENTER),
                    (site.site_name, None, st.CENTER),
                    (preview.month, st.MONTH_FMT, st.CENTER),
                    (vendor.vendor_name, None, st.CENTER),
                    (line.product_name, None, st.LEFT),
                    (qty, qty_fmt, st.CENTER),
                    (line.unit, None, st.CENTER),
                    (line.price, st.MONEY_FMT, st.RIGHT),
                    (line.taxable, st.MONEY_FMT, st.RIGHT),
                    (line.gst_rate / Decimal(100), st.PERCENT_FMT, st.CENTER),
                    (line.gst, st.MONEY_FMT, st.RIGHT),
                    (line.total, st.MONEY_FMT, st.RIGHT),
                ]
                for col, (value, fmt, align) in enumerate(values, start=1):
                    # Site, month and vendor are written once per group, then merged down.
                    if col in (2, 3) and row != site_first:
                        value = None
                    if col == 4 and row != vendor_first:
                        value = None
                    c = ws.cell(row=row, column=col, value=value)
                    c.font = st.BODY_FONT
                    c.alignment = align
                    if fmt:
                        c.number_format = fmt
                _box(ws, row)
                row += 1
            _merge_down(ws, 4, vendor_first, row - 1)
        _merge_down(ws, 2, site_first, row - 1)
        _merge_down(ws, 3, site_first, row - 1)
        t = site.totals
        _total_row(ws, row, f"{site.site_name} TOTAL", t.taxable, t.gst, t.total, st.SUBTOTAL_FILL)
        row += 1

    t = preview.totals
    _total_row(ws, row, "GRAND TOTAL", t.taxable, t.gst, t.total, st.GRAND_FILL)

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:2"


def _vendor_rows(v: VendorDetail) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for i, line in enumerate(v.address_lines):
        rows.append(("Address:" if i == 0 else "", line))
    if v.gstin:
        rows.append(("GSTIN:", v.gstin))
    if v.emails:
        rows.append(("Mail ID:", " | ".join(v.emails)))
    if v.phones:
        rows.append(("Phone:", ", ".join(v.phones)))
    if v.website:
        rows.append(("Website:", v.website))
    if v.drug_licence:
        rows.append(("Drug Licence:", v.drug_licence))
    for i, product in enumerate(v.products_supplied, start=1):
        rows.append(("Products:" if i == 1 else "", f"{i}. {product}"))
    return rows


def _vendor_sheet(ws: Worksheet, preview: Preview) -> None:
    ws.merge_cells("A1:C1")
    title = ws.cell(row=1, column=1, value="VENDOR DETAILS")
    title.font = st.TITLE_FONT
    title.alignment = st.CENTER
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 60

    row = 3
    for n, vendor in enumerate(preview.vendors, start=1):
        first = row
        ws.cell(row=row, column=1, value=n).alignment = st.CENTER
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        name = ws.cell(row=row, column=2, value=vendor.name)
        name.font = st.BOLD
        name.fill = st.HEADER_FILL
        row += 1
        for label, value in _vendor_rows(vendor):
            ws.cell(row=row, column=2, value=label or None).font = st.BOLD
            ws.cell(row=row, column=3, value=value).alignment = st.LEFT
            row += 1
        for r in range(first, row):
            for col in (1, 2, 3):
                ws.cell(row=r, column=col).border = st.BORDER
        if row - 1 > first:
            ws.merge_cells(start_row=first, start_column=1, end_row=row - 1, end_column=1)
            ws.cell(row=first, column=1).alignment = st.CENTER
        row += 1  # blank spacer between vendor blocks


def build_requisition_workbook(preview: Preview) -> bytes:
    wb = Workbook()
    _product_sheet(wb.active, preview)
    _vendor_sheet(wb.create_sheet("Vendor Details"), preview)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
