from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Vendor
from app.schemas.masters import VendorIn, VendorOut, VendorPatch
from app.services.audit import audit

router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("", response_model=list[VendorOut])
async def list_vendors(
    include_inactive: bool = False, session: AsyncSession = Depends(get_session)
):
    stmt = select(Vendor).order_by(Vendor.name)
    if not include_inactive:
        stmt = stmt.where(Vendor.is_active)
    return (await session.scalars(stmt)).all()


@router.get("/{vendor_id}", response_model=VendorOut)
async def get_vendor(vendor_id: int, session: AsyncSession = Depends(get_session)):
    vendor = await session.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(404, "Vendor not found")
    return vendor


@router.post("", response_model=VendorOut, status_code=201)
async def create_vendor(body: VendorIn, session: AsyncSession = Depends(get_session)):
    vendor = Vendor(**body.model_dump())
    session.add(vendor)
    try:
        await session.flush()
    except IntegrityError as e:
        raise HTTPException(409, f"Vendor {body.name!r} already exists") from e
    audit(session, "vendor", vendor.id, "create", new=vendor.name)
    await session.commit()
    return vendor


@router.patch("/{vendor_id}", response_model=VendorOut)
async def update_vendor(
    vendor_id: int, body: VendorPatch, session: AsyncSession = Depends(get_session)
):
    vendor = await session.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(404, "Vendor not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        audit(
            session,
            "vendor",
            vendor.id,
            "update",
            field=field,
            old=getattr(vendor, field),
            new=value,
        )
        setattr(vendor, field, value)
    try:
        await session.commit()
    except IntegrityError as e:
        raise HTTPException(409, "Another vendor already has that name") from e
    await session.refresh(vendor)
    return vendor
