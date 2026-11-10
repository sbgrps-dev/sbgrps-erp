from datetime import date
from decimal import Decimal as D
from io import BytesIO

from openpyxl import load_workbook

from app.excel.price_sheet import PriceRow, build_price_sheet
from app.excel.requisition_workbook import PRODUCT_HEADERS, build_requisition_workbook
from app.schemas.common import Totals
from app.schemas.preview import (
    Preview,
    PreviewLine,
    PreviewSiteGroup,
    PreviewVendorGroup,
    VendorDetail,
)
from app.services.money import line_amounts
from app.services.requisitions import build_filename


def _line(sno, name, qty, price, rate="18", unit="Nos"):
    a = line_amounts(D(qty), D(price), D(rate))
    return PreviewLine(
        sno=sno,
        product_name=name,
        qty=D(qty),
        unit=unit,
        price=D(price),
        gst_rate=D(rate),
        taxable=a.taxable,
        gst=a.gst,
        total=a.total,
    )


def _preview() -> Preview:
    tpj = [_line(1, "Face Mask", "500", "1.25"), _line(2, "Wooden Hand Brush", "50", "68.00")]
    ms_hnr = [_line(3, "APC-F (original)", "100", "75.68", unit="Litres")]
    ms_muthu = [_line(4, "Co-Co Brooms", "24", "30.00", rate="5")]

    def totals(lines):
        t = Totals()
        for ln in lines:
            t.add(ln.taxable, ln.gst, ln.total)
        return t

    sites = [
        PreviewSiteGroup(
            site_id=1,
            site_name="TPJ BIO",
            vendors=[PreviewVendorGroup(vendor_id=1, vendor_name="Muthu Enterprises", lines=tpj)],
            totals=totals(tpj),
        ),
        PreviewSiteGroup(
            site_id=3,
            site_name="MS PFTR & PT",
            vendors=[
                PreviewVendorGroup(
                    vendor_id=7, vendor_name="HNR Corporate Solutions", lines=ms_hnr
                ),
                PreviewVendorGroup(vendor_id=1, vendor_name="Muthu Enterprises", lines=ms_muthu),
            ],
            totals=totals(ms_hnr + ms_muthu),
        ),
    ]
    vendor = VendorDetail(
        vendor_id=1,
        name="Muthu Enterprises",
        address_lines=["No.26, E.H Road", "Vyasarpadi", "Chennai - 600039"],
        gstin="33BXZPM3047C1ZC",
        emails=["a@example.com"],
        phones=["+91 1"],
        website=None,
        drug_licence=None,
        products_supplied=["Tools"],
    )
    return Preview(
        month=date(2026, 11, 1),
        title="SBE STOCK REQUIREMENTS FOR THE MONTH OF NOVEMBER 2026",
        filename=build_filename(["TPJ BIO", "MS PFTR & PT"], date(2026, 11, 1)),
        sites=sites,
        vendors=[vendor],
        totals=totals(tpj + ms_hnr + ms_muthu),
    )


def test_requisition_workbook_layout():
    wb = load_workbook(BytesIO(build_requisition_workbook(_preview())))
    assert wb.sheetnames == ["Product Details", "Vendor Details"]  # no Uniform Details
    ws = wb["Product Details"]
    assert ws["A1"].value == "SBE STOCK REQUIREMENTS FOR THE MONTH OF NOVEMBER 2026"
    assert [c.value for c in ws[2]] == PRODUCT_HEADERS
    merged = {str(r) for r in ws.merged_cells.ranges}
    assert {"A1:L1", "B3:B4", "C3:C4", "D3:D4", "B6:B7", "C6:C7"} <= merged
    assert [ws.cell(row=r, column=1).value for r in (3, 4, 6, 7)] == [1, 2, 3, 4]
    assert ws["C3"].number_format == "mmm-yy"
    assert ws["J3"].value == 0.18 and ws["J3"].number_format == "0%"
    assert ws["A5"].value == "TPJ BIO TOTAL"
    assert ws["A9"].value == "GRAND TOTAL"
    assert D(str(ws["L9"].value)) == D("737.50") + D("4012.00") + D("8930.24") + D("756.00")

    vd = wb["Vendor Details"]
    assert vd["A1"].value == "VENDOR DETAILS"
    assert vd["B3"].value == "Muthu Enterprises"
    assert (vd["B4"].value, vd["C4"].value) == ("Address:", "No.26, E.H Road")


def test_filename_pattern():
    assert (
        build_filename(["TPJ BIO", "MS PFTR & PT"], date(2026, 11, 1))
        == "STOCK REQUIREMENT-TPJ BIO,MS PFTR & PT-NOV-2026.xlsx"
    )
    assert "/" not in build_filename(["A/B"], date(2026, 1, 1))


def test_price_sheet_has_no_quantity_column():
    content = build_price_sheet(
        "Muthu Enterprises",
        date(2026, 11, 10),
        [PriceRow("Face Mask", "Nos", D("1.25"), D("18"), None)],
    )
    ws = load_workbook(BytesIO(content))["Price List"]
    assert [c.value for c in ws[4]] == ["SNO", "Product Name", "Price", "GST %", "HSN"]
    assert ws["C5"].value == D("1.25")
