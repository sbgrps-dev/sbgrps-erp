from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Dec, Totals

QtyField = Field(gt=0, max_digits=12, decimal_places=3)


class LineOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    vendor_id: int
    vendor_name: str
    qty_required: Dec
    unit: str
    price: Dec
    gst_rate: Dec
    taxable_amount: Dec
    gst_amount: Dec
    line_total: Dec
    notes: str | None


class RequisitionOut(BaseModel):
    id: int
    site_id: int
    site_name: str
    month: str
    status: str
    saved_at: datetime | None
    sent_at: datetime | None
    sent_via: str | None
    notes: str | None
    lines: list[LineOut]
    totals: Totals


class MonthSiteSummary(BaseModel):
    site_id: int
    site_code: str
    site_name: str
    requisition_id: int | None
    status: str | None
    line_count: int
    totals: Totals


class MonthSummary(BaseModel):
    month: str
    sites: list[MonthSiteSummary]
    totals: Totals


class LineIn(BaseModel):
    product_id: int
    qty: Decimal = QtyField
    vendor_id: int | None = None
    notes: str | None = None


class LinePatch(BaseModel):
    qty: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    vendor_id: int | None = None
    notes: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    price_reason: str | None = None

    @model_validator(mode="after")
    def price_needs_reason(self) -> "LinePatch":
        if self.price is not None and not (self.price_reason or "").strip():
            raise ValueError("price_reason is required when changing the price")
        return self


class MarkSentIn(BaseModel):
    sent_on: date
    site_ids: list[int] | None = None


class MarkSentOut(BaseModel):
    updated: list[int]
    skipped_not_saved: list[int]


class MonthWorkbookIn(BaseModel):
    site_ids: list[int] | None = None


class WorkbookOut(BaseModel):
    id: int
    month: str
    scope: str
    requisition_id: int | None
    site_ids: list[int]
    version: int
    filename: str
    grand_total: Dec
    created_at: datetime
