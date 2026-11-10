from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from app.db import get_session
from app.excel.price_sheet import PriceRow, build_price_sheet
from app.models import Product, ProductVendor, Vendor
from app.routers.requisitions import XLSX, _attachment

router = APIRouter(prefix="/price-lists", tags=["price-lists"])


@router.get("/vendors/{vendor_id}.xlsx")
async def vendor_price_sheet(
    vendor_id: int,
    product_ids: list[int] | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    vendor = await session.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(404, "Vendor not found")
    stmt = (
        select(ProductVendor)
        .join(Product)
        .where(ProductVendor.vendor_id == vendor_id, Product.is_active)
        .options(contains_eager(ProductVendor.product))
        .order_by(Product.name)
    )
    if product_ids:
        stmt = stmt.where(ProductVendor.product_id.in_(product_ids))
    links = (await session.scalars(stmt)).all()
    if not links:
        raise HTTPException(409, "This vendor has no products linked")
    rows = [
        PriceRow(
            product_name=pv.product.name,
            unit=pv.product.unit,
            price=pv.current_price.price if pv.current_price else None,
            gst_rate=pv.product.gst_rate,
            hsn=pv.product.hsn,
        )
        for pv in links
    ]
    today = date.today()
    content = build_price_sheet(vendor.name, today, rows)
    filename = f"PRICE LIST-{vendor.name.upper()}-{today.strftime('%d-%m-%Y')}.xlsx"
    return Response(
        content=content, media_type=XLSX, headers={"Content-Disposition": _attachment(filename)}
    )
