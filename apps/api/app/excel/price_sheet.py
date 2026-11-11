"""Per-vendor price verification sheet: SNO | Product Name | Price | GST % | HSN. No quantities."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook

from app.excel import styles as st

HEADERS = ["SNO", "Product Name", "Price", "GST %", "HSN"]
WIDTHS = {"A": 6, "B": 44, "C": 12, "D": 8, "E": 12}


@dataclass(frozen=True)
class PriceRow:
    product_name: str
    unit: str
    price: Decimal | None
    gst_rate: Decimal
    hsn: str | None


def build_price_sheet(vendor_name: str, on: date, rows: list[PriceRow]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Price List"
    ws.merge_cells("A1:E1")
    title = ws.cell(row=1, column=1, value=f"PRICE VERIFICATION - {vendor_name.upper()}")
    title.font = st.TITLE_FONT
    title.alignment = st.CENTER
    ws.merge_cells("A2:E2")
    sub = ws.cell(
        row=2,
        column=1,
        value=f"Prices as on {on.strftime('%d-%m-%Y')}. Please confirm or correct each price.",
    )
    sub.alignment = st.CENTER

    for col, header in enumerate(HEADERS, start=1):
        c = ws.cell(row=4, column=col, value=header)
        c.font = st.HEADER_FONT
        c.fill = st.HEADER_FILL
        c.alignment = st.CENTER
        c.border = st.BORDER
    for letter, width in WIDTHS.items():
        ws.column_dimensions[letter].width = width

    for i, r in enumerate(rows, start=1):
        row = 4 + i
        cells = [
            (i, st.INT_FMT, st.CENTER),
            (f"{r.product_name} (per {r.unit})", None, st.LEFT),
            (r.price, st.MONEY_FMT, st.RIGHT),
            (r.gst_rate / Decimal(100), st.PERCENT_FMT, st.CENTER),
            (r.hsn, None, st.CENTER),
        ]
        for col, (value, fmt, align) in enumerate(cells, start=1):
            c = ws.cell(row=row, column=col, value=value)
            c.alignment = align
            c.border = st.BORDER
            if fmt:
                c.number_format = fmt
    ws.freeze_panes = "A5"
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
