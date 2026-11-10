from datetime import UTC, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from app.db import get_session
from app.excel.requisition_workbook import build_requisition_workbook
from app.models import GeneratedWorkbook, Product, RequisitionLine, Site, StockRequisition
from app.schemas.common import Totals
from app.schemas.preview import Preview
from app.schemas.requisitions import (
    LineIn,
    LinePatch,
    MarkSentIn,
    MarkSentOut,
    MonthSiteSummary,
    MonthSummary,
    MonthWorkbookIn,
    RequisitionOut,
    WorkbookOut,
)
from app.services.audit import audit
from app.services.money import line_amounts
from app.services.months import format_month, parse_month
from app.services.prices import set_price
from app.services.requisitions import (
    build_preview,
    ensure_draft,
    get_product_vendor,
    get_requisition,
    requisition_out,
    totals_of,
)

router = APIRouter(tags=["requisitions"])

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _snapshot(line: RequisitionLine, product: Product, price, unit: str | None = None) -> None:
    line.unit_snapshot = unit or product.unit
    line.price_snapshot = price
    line.gst_rate_snapshot = product.gst_rate
    _recompute(line)


def _recompute(line: RequisitionLine) -> None:
    amounts = line_amounts(line.qty_required, line.price_snapshot, line.gst_rate_snapshot)
    line.taxable_amount = amounts.taxable
    line.gst_amount = amounts.gst
    line.line_total = amounts.total


async def _reload(session: AsyncSession, req_id: int) -> RequisitionOut:
    session.expunge_all()
    return requisition_out(await get_requisition(session, req_id))


def _workbook_out(wb: GeneratedWorkbook) -> WorkbookOut:
    return WorkbookOut(
        id=wb.id,
        month=format_month(wb.month),
        scope=wb.scope,
        requisition_id=wb.requisition_id,
        site_ids=wb.site_ids,
        version=wb.version,
        filename=wb.filename,
        grand_total=wb.grand_total,
        created_at=wb.created_at,
    )


async def _store_workbook(
    session: AsyncSession, preview: Preview, scope: str, requisition_id: int | None
) -> GeneratedWorkbook:
    if not preview.sites:
        raise HTTPException(409, "Nothing to generate: no lines for the chosen sites")
    last = await session.scalar(
        select(func.max(GeneratedWorkbook.version)).where(
            GeneratedWorkbook.month == preview.month,
            GeneratedWorkbook.scope == scope,
            GeneratedWorkbook.requisition_id.is_(None)
            if requisition_id is None
            else GeneratedWorkbook.requisition_id == requisition_id,
        )
    )
    wb = GeneratedWorkbook(
        month=preview.month,
        scope=scope,
        requisition_id=requisition_id,
        site_ids=[s.site_id for s in preview.sites],
        version=(last or 0) + 1,
        filename=preview.filename,
        content=build_requisition_workbook(preview),
        grand_total=preview.totals.total,
    )
    session.add(wb)
    await session.flush()
    audit(session, "generated_workbook", wb.id, "generate", new=f"{scope} v{wb.version}")
    await session.commit()
    await session.refresh(wb)
    return wb


async def _month_requisitions(
    session: AsyncSession, month_str: str, site_ids: list[int] | None
) -> tuple:
    month = parse_month(month_str)
    stmt = select(StockRequisition).where(StockRequisition.month == month)
    if site_ids:
        stmt = stmt.where(StockRequisition.site_id.in_(site_ids))
    return month, list((await session.scalars(stmt)).unique().all())


# ---- Month level -------------------------------------------------------------------------


@router.get("/months/{month}/requisitions", response_model=MonthSummary)
async def month_summary(month: str, session: AsyncSession = Depends(get_session)):
    m, reqs = await _month_requisitions(session, month, None)
    by_site = {r.site_id: r for r in reqs}
    sites = (
        await session.scalars(
            select(Site).where(Site.is_active).order_by(Site.sort_order, Site.display_name)
        )
    ).all()
    out: list[MonthSiteSummary] = []
    grand = Totals()
    for site in sites:
        req = by_site.get(site.id)
        t = totals_of(req.lines) if req else Totals()
        grand.add(t.taxable, t.gst, t.total)
        out.append(
            MonthSiteSummary(
                site_id=site.id,
                site_code=site.code,
                site_name=site.display_name,
                requisition_id=req.id if req else None,
                status=req.status if req else None,
                line_count=len(req.lines) if req else 0,
                totals=t,
            )
        )
    return MonthSummary(month=format_month(m), sites=out, totals=grand)


@router.put("/months/{month}/sites/{site_id}/requisition", response_model=RequisitionOut)
async def open_requisition(month: str, site_id: int, session: AsyncSession = Depends(get_session)):
    m = parse_month(month)
    site = await session.get(Site, site_id)
    if site is None:
        raise HTTPException(404, "Site not found")
    req = await session.scalar(
        select(StockRequisition).where(
            StockRequisition.site_id == site_id, StockRequisition.month == m
        )
    )
    if req is None:
        req = StockRequisition(site_id=site_id, month=m, status="draft")
        session.add(req)
        try:
            await session.flush()
        except IntegrityError:  # created concurrently; use that one
            await session.rollback()
            req = await session.scalar(
                select(StockRequisition).where(
                    StockRequisition.site_id == site_id, StockRequisition.month == m
                )
            )
        else:
            audit(session, "stock_requisition", req.id, "create", new=f"{site.code} {month}")
            await session.commit()
    return await _reload(session, req.id)


@router.get("/months/{month}/preview", response_model=Preview)
async def month_preview(
    month: str,
    site_ids: list[int] | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    m, reqs = await _month_requisitions(session, month, site_ids)
    return build_preview(m, reqs)


@router.post("/months/{month}/workbooks", response_model=WorkbookOut, status_code=201)
async def generate_month_workbook(
    month: str, body: MonthWorkbookIn, session: AsyncSession = Depends(get_session)
):
    m, reqs = await _month_requisitions(session, month, body.site_ids)
    return _workbook_out(await _store_workbook(session, build_preview(m, reqs), "month", None))


@router.post("/months/{month}/mark-sent-manually", response_model=MarkSentOut)
async def mark_sent_manually(
    month: str, body: MarkSentIn, session: AsyncSession = Depends(get_session)
):
    _, reqs = await _month_requisitions(session, month, body.site_ids)
    sent_at = datetime.combine(body.sent_on, time(12, 0), tzinfo=UTC)
    updated, skipped = [], []
    for req in reqs:
        if req.status != "saved":
            if req.lines:
                skipped.append(req.id)
            continue
        audit(session, "stock_requisition", req.id, "status", old=req.status, new="sent_manually")
        req.status, req.sent_at, req.sent_via = "sent_manually", sent_at, "manual"
        updated.append(req.id)
    await session.commit()
    return MarkSentOut(updated=updated, skipped_not_saved=skipped)


# ---- Requisition level -------------------------------------------------------------------


@router.get("/requisitions/{req_id}", response_model=RequisitionOut)
async def read_requisition(req_id: int, session: AsyncSession = Depends(get_session)):
    return requisition_out(await get_requisition(session, req_id))


@router.post("/requisitions/{req_id}/lines", response_model=RequisitionOut, status_code=201)
async def add_line(req_id: int, body: LineIn, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    ensure_draft(req)
    product = await session.get(Product, body.product_id)
    if product is None or not product.is_active:
        raise HTTPException(422, "Product not found or inactive")
    pv = await get_product_vendor(session, product.id, body.vendor_id)
    current = pv.current_price
    if current is None:
        raise HTTPException(422, "This vendor has no current price for the product")
    if any(ln.product_id == product.id and ln.vendor_id == pv.vendor_id for ln in req.lines):
        raise HTTPException(409, "This product from this vendor is already on the list")
    line = RequisitionLine(
        requisition_id=req.id,
        product_id=product.id,
        vendor_id=pv.vendor_id,
        qty_required=body.qty,
        notes=body.notes,
    )
    _snapshot(line, product, current.price)
    session.add(line)
    await session.flush()
    audit(session, "requisition_line", line.id, "create", new=f"{product.name} x {body.qty}")
    await session.commit()
    return await _reload(session, req.id)


@router.patch("/requisitions/{req_id}/lines/{line_id}", response_model=RequisitionOut)
async def update_line(
    req_id: int, line_id: int, body: LinePatch, session: AsyncSession = Depends(get_session)
):
    req = await get_requisition(session, req_id)
    ensure_draft(req)
    line = next((ln for ln in req.lines if ln.id == line_id), None)
    if line is None:
        raise HTTPException(404, "Line not found")
    changes = body.model_dump(exclude_unset=True)
    product = line.product

    if "qty" in changes and body.qty is not None:
        audit(
            session,
            "requisition_line",
            line.id,
            "update",
            field="qty",
            old=line.qty_required,
            new=body.qty,
        )
        line.qty_required = body.qty
    if "notes" in changes:
        line.notes = body.notes
    if body.vendor_id is not None and body.vendor_id != line.vendor_id:
        if any(
            ln.product_id == line.product_id and ln.vendor_id == body.vendor_id for ln in req.lines
        ):
            raise HTTPException(409, "This product from that vendor is already on the list")
        pv = await get_product_vendor(session, product.id, body.vendor_id)
        if pv.current_price is None:
            raise HTTPException(422, "That vendor has no current price for the product")
        audit(
            session,
            "requisition_line",
            line.id,
            "update",
            field="vendor_id",
            old=line.vendor_id,
            new=body.vendor_id,
        )
        line.vendor_id = body.vendor_id
        _snapshot(line, product, pv.current_price.price)
    if body.price is not None:
        pv = await get_product_vendor(session, product.id, line.vendor_id)
        await set_price(
            session, pv, body.price, source="office_edit", reason=(body.price_reason or "").strip()
        )
        line.price_snapshot = body.price
    _recompute(line)
    await session.commit()
    return await _reload(session, req.id)


@router.delete("/requisitions/{req_id}/lines/{line_id}", response_model=RequisitionOut)
async def delete_line(req_id: int, line_id: int, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    ensure_draft(req)
    line = next((ln for ln in req.lines if ln.id == line_id), None)
    if line is None:
        raise HTTPException(404, "Line not found")
    audit(session, "requisition_line", line.id, "delete", old=f"{line.product.name}")
    req.lines.remove(line)
    await session.commit()
    return await _reload(session, req.id)


@router.get("/requisitions/{req_id}/preview", response_model=Preview)
async def requisition_preview(req_id: int, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    return build_preview(req.month, [req])


@router.post("/requisitions/{req_id}/workbooks", response_model=WorkbookOut, status_code=201)
async def generate_requisition_workbook(req_id: int, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    preview = build_preview(req.month, [req])
    return _workbook_out(await _store_workbook(session, preview, "site", req.id))


@router.post("/requisitions/{req_id}/save", response_model=RequisitionOut)
async def save_requisition(req_id: int, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    ensure_draft(req)
    if not req.lines:
        raise HTTPException(409, "Add at least one product before saving")
    audit(session, "stock_requisition", req.id, "status", old=req.status, new="saved")
    req.status, req.saved_at = "saved", datetime.now(UTC)
    await session.commit()
    return await _reload(session, req.id)


@router.post("/requisitions/{req_id}/reopen", response_model=RequisitionOut)
async def reopen_requisition(req_id: int, session: AsyncSession = Depends(get_session)):
    req = await get_requisition(session, req_id)
    if req.status != "saved":
        raise HTTPException(409, f"Only a saved requisition can be reopened (it is {req.status})")
    audit(session, "stock_requisition", req.id, "status", old=req.status, new="draft")
    req.status = "draft"
    await session.commit()
    return await _reload(session, req.id)


# ---- Workbooks ---------------------------------------------------------------------------


@router.get("/workbooks", response_model=list[WorkbookOut])
async def list_workbooks(
    month: str | None = None,
    requisition_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(GeneratedWorkbook).order_by(GeneratedWorkbook.created_at.desc()).limit(200)
    if month:
        stmt = stmt.where(GeneratedWorkbook.month == parse_month(month))
    if requisition_id is not None:
        stmt = stmt.where(GeneratedWorkbook.requisition_id == requisition_id)
    return [_workbook_out(wb) for wb in (await session.scalars(stmt)).all()]


@router.get("/workbooks/{workbook_id}/download")
async def download_workbook(workbook_id: int, session: AsyncSession = Depends(get_session)):
    wb = await session.scalar(
        select(GeneratedWorkbook)
        .where(GeneratedWorkbook.id == workbook_id)
        .options(undefer(GeneratedWorkbook.content))
    )
    if wb is None:
        raise HTTPException(404, "Workbook not found")
    return Response(
        content=wb.content,
        media_type=XLSX,
        headers={"Content-Disposition": _attachment(wb.filename)},
    )


def _attachment(filename: str) -> str:
    from urllib.parse import quote

    ascii_name = filename.encode("ascii", "replace").decode().replace('"', "")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"
