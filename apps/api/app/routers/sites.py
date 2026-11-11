from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Site
from app.schemas.masters import SiteIn, SiteOut, SitePatch
from app.services.audit import audit

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=list[SiteOut])
async def list_sites(include_inactive: bool = False, session: AsyncSession = Depends(get_session)):
    stmt = select(Site).order_by(Site.sort_order, Site.display_name)
    if not include_inactive:
        stmt = stmt.where(Site.is_active)
    return (await session.scalars(stmt)).all()


@router.post("", response_model=SiteOut, status_code=201)
async def create_site(body: SiteIn, session: AsyncSession = Depends(get_session)):
    site = Site(**body.model_dump())
    session.add(site)
    try:
        await session.flush()
    except IntegrityError as e:
        raise HTTPException(409, f"Site code {body.code!r} already exists") from e
    audit(session, "site", site.id, "create", new=site.display_name)
    await session.commit()
    return site


@router.patch("/{site_id}", response_model=SiteOut)
async def update_site(site_id: int, body: SitePatch, session: AsyncSession = Depends(get_session)):
    site = await session.get(Site, site_id)
    if site is None:
        raise HTTPException(404, "Site not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        audit(session, "site", site.id, "update", field=field, old=getattr(site, field), new=value)
        setattr(site, field, value)
    await session.commit()
    await session.refresh(site)
    return site
