from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exists, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Product, ProductPrice, ProductVendor, Vendor
from app.schemas.masters import (
    NewPriceIn,
    PriceOut,
    ProductIn,
    ProductOut,
    ProductPatch,
    VendorPriceIn,
)
from app.services.audit import audit
from app.services.prices import _SEARCH_STRIP, normalise, set_price
from app.services.requisitions import get_product_vendor, product_out

router = APIRouter(prefix="/products", tags=["products"])


def _norm_sql(col):
    return func.regexp_replace(func.lower(col), _SEARCH_STRIP, "", "g")


async def _load(session: AsyncSession, product_id: int) -> Product:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


async def _ensure_vendor(session: AsyncSession, vendor_id: int) -> None:
    if await session.get(Vendor, vendor_id) is None:
        raise HTTPException(422, f"Vendor {vendor_id} not found")


async def _make_preferred(session: AsyncSession, product: Product, vendor_id: int) -> None:
    await session.execute(
        update(ProductVendor)
        .where(ProductVendor.product_id == product.id, ProductVendor.is_preferred)
        .values(is_preferred=False)
    )
    await session.flush()
    await session.execute(
        update(ProductVendor)
        .where(ProductVendor.product_id == product.id, ProductVendor.vendor_id == vendor_id)
        .values(is_preferred=True)
    )
    await session.flush()
    await session.refresh(product, ["vendors"])


@router.get("", response_model=list[ProductOut])
async def search_products(
    q: str | None = None,
    vendor_id: int | None = None,
    include_inactive: bool = False,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Product).order_by(Product.name).limit(min(max(limit, 1), 500))
    if not include_inactive:
        stmt = stmt.where(Product.is_active)
    if q and (key := normalise(q)):
        pattern = f"%{key}%"
        alias = func.unnest(Product.aliases).table_valued("value").render_derived()
        stmt = stmt.where(
            _norm_sql(Product.name).like(pattern)
            | _norm_sql(Product.code).like(pattern)
            | exists(select(1).select_from(alias).where(_norm_sql(alias.c.value).like(pattern)))
        )
    if vendor_id is not None:
        stmt = stmt.where(Product.vendors.any(ProductVendor.vendor_id == vendor_id))
    return [product_out(p) for p in (await session.scalars(stmt)).all()]


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return product_out(await _load(session, product_id))


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(body: ProductIn, session: AsyncSession = Depends(get_session)):
    vendor_ids = [v.vendor_id for v in body.vendors]
    if len(set(vendor_ids)) != len(vendor_ids):
        raise HTTPException(422, "Each vendor can be listed once")
    for vid in vendor_ids:
        await _ensure_vendor(session, vid)
    preferred = next((v.vendor_id for v in body.vendors if v.is_preferred), vendor_ids[0])

    product = Product(
        code=body.code or f"TMP-{uuid4().hex[:12]}",
        name=body.name.strip(),
        aliases=body.aliases,
        unit=body.unit.strip(),
        hsn=body.hsn,
        gst_rate=body.gst_rate,
    )
    session.add(product)
    try:
        await session.flush()
    except IntegrityError as e:
        raise HTTPException(409, f"Product code {body.code!r} already exists") from e
    if not body.code:
        product.code = f"P{product.id:04d}"
    for v in body.vendors:
        pv = ProductVendor(
            product_id=product.id, vendor_id=v.vendor_id, is_preferred=v.vendor_id == preferred
        )
        session.add(pv)
        await session.flush()
        session.add(
            ProductPrice(
                product_vendor_id=pv.id,
                price=v.price,
                effective_from=date.today(),
                source="office_edit",
                reason="new product",
            )
        )
    audit(session, "product", product.id, "create", new=product.name)
    await session.commit()
    session.expunge(product)
    return product_out(await _load(session, product.id))


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int, body: ProductPatch, session: AsyncSession = Depends(get_session)
):
    product = await _load(session, product_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        audit(
            session,
            "product",
            product.id,
            "update",
            field=field,
            old=getattr(product, field),
            new=value,
        )
        setattr(product, field, value)
    await session.commit()
    await session.refresh(product)
    return product_out(product)


@router.post("/{product_id}/vendors", response_model=ProductOut, status_code=201)
async def link_vendor(
    product_id: int, body: VendorPriceIn, session: AsyncSession = Depends(get_session)
):
    product = await _load(session, product_id)
    await _ensure_vendor(session, body.vendor_id)
    if any(pv.vendor_id == body.vendor_id for pv in product.vendors):
        raise HTTPException(409, "Vendor already linked to this product")
    pv = ProductVendor(product_id=product.id, vendor_id=body.vendor_id, is_preferred=False)
    session.add(pv)
    await session.flush()
    await session.refresh(pv, ["prices"])
    await set_price(session, pv, body.price, source="office_edit", reason="vendor linked")
    if body.is_preferred or len(product.vendors) == 0:
        await _make_preferred(session, product, body.vendor_id)
    audit(session, "product", product.id, "link_vendor", new=body.vendor_id)
    await session.commit()
    await session.refresh(product, ["vendors"])
    return product_out(product)


@router.post("/{product_id}/vendors/{vendor_id}/prices", response_model=ProductOut)
async def new_price(
    product_id: int,
    vendor_id: int,
    body: NewPriceIn,
    session: AsyncSession = Depends(get_session),
):
    product = await _load(session, product_id)
    pv = await get_product_vendor(session, product_id, vendor_id)
    await set_price(
        session,
        pv,
        body.price,
        source="office_edit",
        reason=body.reason.strip(),
        effective_from=body.effective_from,
    )
    if body.make_preferred:
        await _make_preferred(session, product, vendor_id)
    await session.commit()
    await session.refresh(product, ["vendors"])
    return product_out(product)


@router.get("/{product_id}/prices", response_model=dict[str, list[PriceOut]])
async def price_history(product_id: int, session: AsyncSession = Depends(get_session)):
    """Price history per vendor name, newest first."""
    product = await _load(session, product_id)
    return {
        pv.vendor.name: [PriceOut.model_validate(p) for p in pv.prices] for pv in product.vendors
    }
