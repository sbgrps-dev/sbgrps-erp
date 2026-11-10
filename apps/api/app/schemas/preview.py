"""The review pane and the Excel generator both read this structure."""

from datetime import date

from pydantic import BaseModel

from app.schemas.common import Dec, Totals


class PreviewLine(BaseModel):
    sno: int
    product_name: str
    qty: Dec
    unit: str
    price: Dec
    gst_rate: Dec
    taxable: Dec
    gst: Dec
    total: Dec


class PreviewVendorGroup(BaseModel):
    vendor_id: int
    vendor_name: str
    lines: list[PreviewLine]


class PreviewSiteGroup(BaseModel):
    site_id: int
    site_name: str
    vendors: list[PreviewVendorGroup]
    totals: Totals


class VendorDetail(BaseModel):
    vendor_id: int
    name: str
    address_lines: list[str]
    gstin: str | None
    emails: list[str]
    phones: list[str]
    website: str | None
    drug_licence: str | None
    products_supplied: list[str]


class Preview(BaseModel):
    month: date
    title: str
    filename: str
    sites: list[PreviewSiteGroup]
    vendors: list[VendorDetail]
    totals: Totals
