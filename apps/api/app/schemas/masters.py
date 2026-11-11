from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import ORM, Dec


def _clean_list(values: list[str]) -> list[str]:
    seen: list[str] = []
    for v in values:
        v = v.strip()
        if v and v not in seen:
            seen.append(v)
    return seen


class SiteIn(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    display_name: str = Field(min_length=1, max_length=120)
    sort_order: int = 100


class SitePatch(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    sort_order: int | None = None
    is_active: bool | None = None


class SiteOut(ORM):
    id: int
    code: str
    display_name: str
    is_active: bool
    sort_order: int


class VendorIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    address: str | None = None
    gstin: str | None = Field(default=None, max_length=20)
    emails: list[str] = []
    phones: list[str] = []
    website: str | None = None
    drug_licence: str | None = None
    products_supplied: str | None = None

    _clean = field_validator("emails", "phones")(_clean_list)


class VendorPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    address: str | None = None
    gstin: str | None = Field(default=None, max_length=20)
    emails: list[str] | None = None
    phones: list[str] | None = None
    website: str | None = None
    drug_licence: str | None = None
    products_supplied: str | None = None
    is_active: bool | None = None


class VendorOut(ORM):
    id: int
    name: str
    address: str | None
    gstin: str | None
    emails: list[str]
    phones: list[str]
    website: str | None
    drug_licence: str | None
    products_supplied: str | None
    is_active: bool


class PriceOut(ORM):
    id: int
    price: Dec
    effective_from: date
    effective_to: date | None
    source: str
    reason: str | None


class ProductVendorOut(BaseModel):
    vendor_id: int
    vendor_name: str
    is_preferred: bool
    current_price: Dec | None


class ProductOut(BaseModel):
    id: int
    code: str
    name: str
    aliases: list[str]
    unit: str
    hsn: str | None
    gst_rate: Dec
    is_active: bool
    vendors: list[ProductVendorOut]


class VendorPriceIn(BaseModel):
    vendor_id: int
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    is_preferred: bool = False


class ProductIn(BaseModel):
    code: str | None = Field(default=None, max_length=40)
    name: str = Field(min_length=1, max_length=200)
    aliases: list[str] = []
    unit: str = Field(min_length=1, max_length=30)
    hsn: str | None = Field(default=None, max_length=12)
    gst_rate: Decimal = Field(default=Decimal("18"), ge=0, le=28, decimal_places=2)
    vendors: list[VendorPriceIn] = Field(min_length=1)

    _clean = field_validator("aliases")(_clean_list)


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    aliases: list[str] | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    hsn: str | None = Field(default=None, max_length=12)
    gst_rate: Decimal | None = Field(default=None, ge=0, le=28, decimal_places=2)
    is_active: bool | None = None


class NewPriceIn(BaseModel):
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    reason: str = Field(min_length=1)
    effective_from: date | None = None
    make_preferred: bool = False
