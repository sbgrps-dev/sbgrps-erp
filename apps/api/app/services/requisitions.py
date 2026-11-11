import re
from collections import defaultdict
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Product, ProductVendor, RequisitionLine, StockRequisition, Vendor
from app.schemas.common import Totals
from app.schemas.masters import ProductOut, ProductVendorOut
from app.schemas.preview import (
    Preview,
    PreviewLine,
    PreviewSiteGroup,
    PreviewVendorGroup,
    VendorDetail,
)
from app.schemas.requisitions import LineOut, RequisitionOut
from app.services.months import format_month

_BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]+')


async def get_requisition(session: AsyncSession, requisition_id: int) -> StockRequisition:
    req = await session.get(StockRequisition, requisition_id)
    if req is None:
        raise HTTPException(404, "Requisition not found")
    return req


def ensure_draft(req: StockRequisition) -> None:
    if req.status != "draft":
        raise HTTPException(409, f"Requisition is {req.status}; reopen it before changing lines")


def totals_of(lines: list[RequisitionLine]) -> Totals:
    t = Totals()
    for line in lines:
        t.add(line.taxable_amount, line.gst_amount, line.line_total)
    return t


def requisition_out(req: StockRequisition) -> RequisitionOut:
    return RequisitionOut(
        id=req.id,
        site_id=req.site_id,
        site_name=req.site.display_name,
        month=format_month(req.month),
        status=req.status,
        saved_at=req.saved_at,
        sent_at=req.sent_at,
        sent_via=req.sent_via,
        notes=req.notes,
        lines=[
            LineOut(
                id=line.id,
                product_id=line.product_id,
                product_name=line.product.name,
                vendor_id=line.vendor_id,
                vendor_name=line.vendor.name,
                qty_required=line.qty_required,
                unit=line.unit_snapshot,
                price=line.price_snapshot,
                gst_rate=line.gst_rate_snapshot,
                taxable_amount=line.taxable_amount,
                gst_amount=line.gst_amount,
                line_total=line.line_total,
                notes=line.notes,
            )
            for line in req.lines
        ],
        totals=totals_of(req.lines),
    )


def product_out(product: Product) -> ProductOut:
    vendors = sorted(product.vendors, key=lambda pv: (not pv.is_preferred, pv.vendor.name.lower()))
    return ProductOut(
        id=product.id,
        code=product.code,
        name=product.name,
        aliases=product.aliases,
        unit=product.unit,
        hsn=product.hsn,
        gst_rate=product.gst_rate,
        is_active=product.is_active,
        vendors=[
            ProductVendorOut(
                vendor_id=pv.vendor_id,
                vendor_name=pv.vendor.name,
                is_preferred=pv.is_preferred,
                current_price=pv.current_price.price if pv.current_price else None,
            )
            for pv in vendors
        ],
    )


async def get_product_vendor(
    session: AsyncSession, product_id: int, vendor_id: int | None
) -> ProductVendor:
    """The approved (product, vendor) link; preferred vendor when vendor_id is None."""
    stmt = select(ProductVendor).where(ProductVendor.product_id == product_id)
    if vendor_id is None:
        stmt = stmt.order_by(ProductVendor.is_preferred.desc(), ProductVendor.id).limit(1)
    else:
        stmt = stmt.where(ProductVendor.vendor_id == vendor_id)
    pv = (await session.scalars(stmt)).first()
    if pv is None:
        if vendor_id is None:
            raise HTTPException(422, "Product has no approved vendor; link a vendor first")
        raise HTTPException(422, "That vendor is not an approved vendor for this product")
    return pv


def build_filename(site_names: list[str], month: date) -> str:
    sites = ",".join(site_names) or "NO SITES"
    name = f"STOCK REQUIREMENT-{sites}-{month.strftime('%b').upper()}-{month.year}.xlsx"
    return _BAD_FILENAME_CHARS.sub("-", name)


def build_title(month: date) -> str:
    company = get_settings().company_short_name
    return (
        f"{company} STOCK REQUIREMENTS FOR THE MONTH OF {month.strftime('%B').upper()} {month.year}"
    )


def vendor_detail(v: Vendor) -> VendorDetail:
    products = [p.strip() for p in re.split(r"[\n;]+", v.products_supplied or "") if p.strip()]
    return VendorDetail(
        vendor_id=v.id,
        name=v.name,
        address_lines=[ln.strip() for ln in (v.address or "").splitlines() if ln.strip()],
        gstin=v.gstin,
        emails=v.emails,
        phones=v.phones,
        website=v.website,
        drug_licence=v.drug_licence,
        products_supplied=products,
    )


def build_preview(month: date, requisitions: list[StockRequisition]) -> Preview:
    """Group lines by site (sort_order), then vendor, then product; number SNO 1..n."""
    reqs = sorted(
        (r for r in requisitions if r.lines),
        key=lambda r: (r.site.sort_order, r.site.display_name.lower()),
    )
    sno = 0
    sites: list[PreviewSiteGroup] = []
    vendors_seen: dict[int, Vendor] = {}
    grand = Totals()
    for req in reqs:
        by_vendor: dict[int, list[RequisitionLine]] = defaultdict(list)
        for line in req.lines:
            by_vendor[line.vendor_id].append(line)
            vendors_seen.setdefault(line.vendor_id, line.vendor)
        groups: list[PreviewVendorGroup] = []
        site_totals = Totals()
        for vendor_id in sorted(by_vendor, key=lambda vid: vendors_seen[vid].name.lower()):
            rows: list[PreviewLine] = []
            for line in sorted(by_vendor[vendor_id], key=lambda ln: ln.product.name.lower()):
                sno += 1
                rows.append(
                    PreviewLine(
                        sno=sno,
                        product_name=line.product.name,
                        qty=line.qty_required,
                        unit=line.unit_snapshot,
                        price=line.price_snapshot,
                        gst_rate=line.gst_rate_snapshot,
                        taxable=line.taxable_amount,
                        gst=line.gst_amount,
                        total=line.line_total,
                    )
                )
                site_totals.add(line.taxable_amount, line.gst_amount, line.line_total)
            groups.append(
                PreviewVendorGroup(
                    vendor_id=vendor_id, vendor_name=vendors_seen[vendor_id].name, lines=rows
                )
            )
        grand.add(site_totals.taxable, site_totals.gst, site_totals.total)
        sites.append(
            PreviewSiteGroup(
                site_id=req.site_id,
                site_name=req.site.display_name,
                vendors=groups,
                totals=site_totals,
            )
        )
    vendor_order = sorted(vendors_seen.values(), key=lambda v: v.name.lower())
    return Preview(
        month=month,
        title=build_title(month),
        filename=build_filename([s.site_name for s in sites], month),
        sites=sites,
        vendors=[vendor_detail(v) for v in vendor_order],
        totals=grand,
    )
