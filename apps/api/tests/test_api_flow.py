from io import BytesIO

import pytest
from openpyxl import load_workbook

pytestmark = pytest.mark.db

A = "/api/v1"


async def _site(client, code):
    sites = (await client.get(f"{A}/sites")).json()
    return next(s for s in sites if s["code"] == code)


async def _product(client, q):
    found = (await client.get(f"{A}/products", params={"q": q})).json()
    assert found, q
    return found[0]


async def test_search_is_alias_aware(client):
    for q in ["STERIX A SUPER", "sterix-a", "Sterix"]:
        assert (await _product(client, q))["code"] == "STERIX-A"
    assert (await _product(client, "surgical gloves"))["code"] == "GLOVE-SURG"


async def test_monthly_requisition_flow(client):
    ms = await _site(client, "MSPFTR_PT")
    tpj = await _site(client, "TPJ_BIO")
    req = (await client.put(f"{A}/months/2026-11/sites/{ms['id']}/requisition")).json()
    assert req["status"] == "draft" and req["lines"] == []
    # get-or-create is idempotent
    again = (await client.put(f"{A}/months/2026-11/sites/{ms['id']}/requisition")).json()
    assert again["id"] == req["id"]
    rid = req["id"]

    apcf = await _product(client, "apc-f original")
    sterix = await _product(client, "sterix")
    r = await client.post(
        f"{A}/requisitions/{rid}/lines", json={"product_id": apcf["id"], "qty": 100}
    )
    assert r.status_code == 201, r.text
    line = r.json()["lines"][0]
    assert (line["price"], line["taxable_amount"], line["gst_amount"], line["line_total"]) == (
        "75.68",
        "7568.00",
        "1362.24",
        "8930.24",
    )

    # Default vendor = preferred (HNR); switching to Transchem re-snapshots the price.
    r = await client.post(
        f"{A}/requisitions/{rid}/lines", json={"product_id": sterix["id"], "qty": 10}
    )
    sterix_line = next(ln for ln in r.json()["lines"] if ln["product_id"] == sterix["id"])
    assert sterix_line["vendor_name"] == "HNR Corporate Solutions"
    transchem = next(v for v in sterix["vendors"] if v["vendor_name"] == "Transchem")
    r = await client.patch(
        f"{A}/requisitions/{rid}/lines/{sterix_line['id']}",
        json={"vendor_id": transchem["vendor_id"]},
    )
    assert r.status_code == 200, r.text
    sterix_line = next(ln for ln in r.json()["lines"] if ln["id"] == sterix_line["id"])
    assert (sterix_line["price"], sterix_line["line_total"]) == ("30.00", "354.00")

    # Duplicate (product, vendor) is rejected.
    r = await client.post(
        f"{A}/requisitions/{rid}/lines", json={"product_id": apcf["id"], "qty": 5}
    )
    assert r.status_code == 409

    # Price edit needs a reason, writes history, re-snapshots the line.
    r = await client.patch(f"{A}/requisitions/{rid}/lines/{line['id']}", json={"price": "80.00"})
    assert r.status_code == 422
    r = await client.patch(
        f"{A}/requisitions/{rid}/lines/{line['id']}",
        json={"price": "80.00", "price_reason": "HNR revised rate", "qty": "50"},
    )
    line = next(ln for ln in r.json()["lines"] if ln["id"] == line["id"])
    assert (line["price"], line["taxable_amount"]) == ("80.00", "4000.00")
    history = (await client.get(f"{A}/products/{apcf['id']}/prices")).json()
    hnr = history["HNR Corporate Solutions"]
    assert [p["price"] for p in hnr] == ["80.00", "75.68"]
    assert hnr[0]["effective_to"] is None and hnr[1]["effective_to"] is not None

    # Save, then edits are blocked until reopened.
    assert (await client.post(f"{A}/requisitions/{rid}/save")).json()["status"] == "saved"
    r = await client.post(
        f"{A}/requisitions/{rid}/lines", json={"product_id": apcf["id"], "qty": 1}
    )
    assert r.status_code == 409
    assert (await client.post(f"{A}/requisitions/{rid}/reopen")).json()["status"] == "draft"
    assert (await client.post(f"{A}/requisitions/{rid}/save")).status_code == 200

    # Second site (left as draft) so the month workbook covers two sites.
    t = (await client.put(f"{A}/months/2026-11/sites/{tpj['id']}/requisition")).json()
    mask = await _product(client, "face mask")
    await client.post(
        f"{A}/requisitions/{t['id']}/lines", json={"product_id": mask["id"], "qty": 500}
    )

    preview = (await client.get(f"{A}/months/2026-11/preview")).json()
    assert [s["site_name"] for s in preview["sites"]] == ["TPJ BIO", "MS PFTR & PT"]
    assert [ln["sno"] for s in preview["sites"] for v in s["vendors"] for ln in v["lines"]] == [
        1,
        2,
        3,
    ]

    wb1 = (await client.post(f"{A}/months/2026-11/workbooks", json={})).json()
    wb2 = (await client.post(f"{A}/months/2026-11/workbooks", json={})).json()
    assert (wb1["version"], wb2["version"]) == (1, 2)
    assert wb1["filename"] == "STOCK REQUIREMENT-TPJ BIO,MS PFTR & PT-NOV-2026.xlsx"
    site_wb = (await client.post(f"{A}/requisitions/{rid}/workbooks")).json()
    assert site_wb["version"] == 1 and site_wb["scope"] == "site"

    dl = await client.get(f"{A}/workbooks/{wb2['id']}/download")
    assert dl.status_code == 200
    assert "attachment" in dl.headers["content-disposition"]
    book = load_workbook(BytesIO(dl.content))
    assert book.sheetnames == ["Product Details", "Vendor Details"]
    names = [c.value for c in book["Vendor Details"]["B"] if c.value]
    assert "HNR Corporate Solutions" in names and "Transchem" in names

    summary = (await client.get(f"{A}/months/2026-11/requisitions")).json()
    by_code = {s["site_code"]: s for s in summary["sites"]}
    assert by_code["MSPFTR_PT"]["status"] == "saved"
    assert by_code["SRR"]["requisition_id"] is None

    sent = (
        await client.post(f"{A}/months/2026-11/mark-sent-manually", json={"sent_on": "2026-11-10"})
    ).json()
    assert sent == {"updated": [rid], "skipped_not_saved": [t["id"]]}
    assert (await client.get(f"{A}/requisitions/{rid}")).json()["status"] == "sent_manually"


async def test_inline_new_product_and_price_sheet(client):
    vendors = (await client.get(f"{A}/vendors")).json()
    muthu = next(v for v in vendors if v["name"] == "Muthu Enterprises")
    r = await client.post(
        f"{A}/products",
        json={
            "name": "Harpic 1L",
            "aliases": ["harpic"],
            "unit": "Bottle",
            "vendors": [{"vendor_id": muthu["id"], "price": "185.00"}],
        },
    )
    assert r.status_code == 201, r.text
    p = r.json()
    assert p["code"].startswith("P") and p["vendors"][0]["is_preferred"]

    sheet = await client.get(f"{A}/price-lists/vendors/{muthu['id']}.xlsx")
    assert sheet.status_code == 200
    ws = load_workbook(BytesIO(sheet.content))["Price List"]
    products = [ws.cell(row=r, column=2).value for r in range(5, ws.max_row + 1)]
    assert "Harpic 1L (per Bottle)" in products
