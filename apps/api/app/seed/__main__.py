"""Idempotent seed: `python -m app.seed`. Existing rows (matched by code / name) are left alone."""

import asyncio
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal, engine
from app.models import Product, ProductPrice, ProductVendor, Site, Vendor
from app.seed.data import PRODUCTS, SITES, VENDORS

SEED_DATE = date(2026, 11, 1)


async def seed(session: AsyncSession) -> dict[str, int]:
    created = {"sites": 0, "vendors": 0, "products": 0}
    for code, name, order in SITES:
        if await session.scalar(select(Site).where(Site.code == code)) is None:
            session.add(Site(code=code, display_name=name, sort_order=order))
            created["sites"] += 1

    vendors: dict[str, Vendor] = {}
    for data in VENDORS:
        vendor = await session.scalar(
            select(Vendor).where(func.lower(Vendor.name) == data["name"].lower())
        )
        if vendor is None:
            vendor = Vendor(**data)
            session.add(vendor)
            created["vendors"] += 1
        vendors[data["name"]] = vendor
    await session.flush()

    for code, name, aliases, unit, gst, links in PRODUCTS:
        if await session.scalar(select(Product).where(Product.code == code)) is not None:
            continue
        product = Product(code=code, name=name, aliases=aliases, unit=unit, gst_rate=Decimal(gst))
        session.add(product)
        await session.flush()
        for vendor_name, price, preferred in links:
            pv = ProductVendor(
                product_id=product.id, vendor_id=vendors[vendor_name].id, is_preferred=preferred
            )
            session.add(pv)
            await session.flush()
            session.add(
                ProductPrice(
                    product_vendor_id=pv.id,
                    price=price,
                    effective_from=SEED_DATE,
                    source="seed",
                    reason="Nov-26 requisition file",
                )
            )
        created["products"] += 1
    await session.commit()
    return created


async def main() -> None:
    async with SessionLocal() as session:
        print("Seeded:", await seed(session))
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
