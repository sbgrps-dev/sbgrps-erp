from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin
from app.models.core import Site

MONEY = Numeric(12, 2)
QTY = Numeric(12, 3)
RATE = Numeric(5, 2)

REQ_STATUSES = ("draft", "saved", "sent_to_hq", "sent_manually", "closed")
PRICE_SOURCES = ("seed", "office_edit", "vendor_reply")


class Vendor(IdMixin, TimestampMixin, Base):
    __tablename__ = "vendor"
    __table_args__ = (Index("uq_vendor_name_lower", text("lower(name)"), unique=True),)

    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str | None] = mapped_column(Text)
    gstin: Mapped[str | None] = mapped_column(String(20))
    emails: Mapped[list[str]] = mapped_column(ARRAY(String(160)), default=list, server_default="{}")
    phones: Mapped[list[str]] = mapped_column(ARRAY(String(40)), default=list, server_default="{}")
    website: Mapped[str | None] = mapped_column(String(160))
    drug_licence: Mapped[str | None] = mapped_column(String(80))
    products_supplied: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Product(IdMixin, TimestampMixin, Base):
    __tablename__ = "product"
    __table_args__ = (CheckConstraint("gst_rate >= 0 AND gst_rate <= 28", name="gst_rate_range"),)

    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    aliases: Mapped[list[str]] = mapped_column(
        ARRAY(String(200)), default=list, server_default="{}"
    )
    unit: Mapped[str] = mapped_column(String(30))
    hsn: Mapped[str | None] = mapped_column(String(12))
    gst_rate: Mapped[Decimal] = mapped_column(RATE, default=Decimal("18"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    vendors: Mapped[list["ProductVendor"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )


class ProductVendor(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_vendor"
    __table_args__ = (
        UniqueConstraint("product_id", "vendor_id"),
        Index(
            "uq_product_vendor_one_preferred",
            "product_id",
            unique=True,
            postgresql_where=text("is_preferred"),
        ),
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id", ondelete="RESTRICT"), index=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    product: Mapped[Product] = relationship(back_populates="vendors")
    vendor: Mapped[Vendor] = relationship(lazy="joined")
    prices: Mapped[list["ProductPrice"]] = relationship(
        back_populates="product_vendor",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ProductPrice.effective_from.desc(), ProductPrice.id.desc()",
    )

    @property
    def current_price(self) -> "ProductPrice | None":
        return next((p for p in self.prices if p.effective_to is None), None)


class ProductPrice(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_price"
    __table_args__ = (
        CheckConstraint("price >= 0", name="price_non_negative"),
        CheckConstraint(f"source IN {PRICE_SOURCES}", name="source_valid"),
        Index(
            "uq_product_price_one_current",
            "product_vendor_id",
            unique=True,
            postgresql_where=text("effective_to IS NULL"),
        ),
    )

    product_vendor_id: Mapped[int] = mapped_column(
        ForeignKey("product_vendor.id", ondelete="CASCADE")
    )
    price: Mapped[Decimal] = mapped_column(MONEY)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(Text)

    product_vendor: Mapped[ProductVendor] = relationship(back_populates="prices")


class StockRequisition(IdMixin, TimestampMixin, Base):
    __tablename__ = "stock_requisition"
    __table_args__ = (
        UniqueConstraint("site_id", "month"),
        CheckConstraint(f"status IN {REQ_STATUSES}", name="status_valid"),
        CheckConstraint("extract(day from month) = 1", name="month_is_first_day"),
    )

    site_id: Mapped[int] = mapped_column(ForeignKey("site.id", ondelete="RESTRICT"))
    month: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft")
    saved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_via: Mapped[str | None] = mapped_column(String(10))
    notes: Mapped[str | None] = mapped_column(Text)

    site: Mapped[Site] = relationship(lazy="joined")
    lines: Mapped[list["RequisitionLine"]] = relationship(
        back_populates="requisition",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RequisitionLine.id",
    )


class RequisitionLine(IdMixin, TimestampMixin, Base):
    __tablename__ = "requisition_line"
    __table_args__ = (
        UniqueConstraint("requisition_id", "product_id", "vendor_id"),
        CheckConstraint("qty_required > 0", name="qty_positive"),
    )

    requisition_id: Mapped[int] = mapped_column(
        ForeignKey("stock_requisition.id", ondelete="CASCADE")
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="RESTRICT"), index=True
    )
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id", ondelete="RESTRICT"), index=True)
    qty_required: Mapped[Decimal] = mapped_column(QTY)
    unit_snapshot: Mapped[str] = mapped_column(String(30))
    price_snapshot: Mapped[Decimal] = mapped_column(MONEY)
    gst_rate_snapshot: Mapped[Decimal] = mapped_column(RATE)
    taxable_amount: Mapped[Decimal] = mapped_column(MONEY)
    gst_amount: Mapped[Decimal] = mapped_column(MONEY)
    line_total: Mapped[Decimal] = mapped_column(MONEY)
    notes: Mapped[str | None] = mapped_column(Text)

    requisition: Mapped[StockRequisition] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship(lazy="joined")
    vendor: Mapped[Vendor] = relationship(lazy="joined")


class GeneratedWorkbook(IdMixin, TimestampMixin, Base):
    __tablename__ = "generated_workbook"
    __table_args__ = (
        CheckConstraint("scope IN ('site', 'month')", name="scope_valid"),
        CheckConstraint(
            "(scope = 'site') = (requisition_id IS NOT NULL)", name="site_scope_has_requisition"
        ),
        UniqueConstraint(
            "month", "scope", "requisition_id", "version", postgresql_nulls_not_distinct=True
        ),
    )

    month: Mapped[date] = mapped_column(Date)
    scope: Mapped[str] = mapped_column(String(10))
    requisition_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_requisition.id", ondelete="CASCADE"), index=True
    )
    site_ids: Mapped[list[int]] = mapped_column(ARRAY(BigInteger))
    version: Mapped[int] = mapped_column(Integer)
    filename: Mapped[str] = mapped_column(String(255))
    content: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    grand_total: Mapped[Decimal] = mapped_column(MONEY)
