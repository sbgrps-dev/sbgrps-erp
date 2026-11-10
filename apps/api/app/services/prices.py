import re
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProductPrice, ProductVendor
from app.services.audit import audit

_SEARCH_STRIP = r"[\s\-\.\(\)_/&',]+"


def normalise(text: str) -> str:
    """Search key: lower-case, no spaces or punctuation. 'STERIX-A super' -> 'sterixasuper'."""
    return re.sub(_SEARCH_STRIP, "", text.lower())


async def set_price(
    session: AsyncSession,
    pv: ProductVendor,
    price: Decimal,
    *,
    source: str,
    reason: str | None,
    effective_from: date | None = None,
) -> ProductPrice:
    """Close the current price (kept as history) and open a new one."""
    start = effective_from or date.today()
    current = pv.current_price
    old_value = current.price if current else None
    if current is not None:
        current.effective_to = max(start, current.effective_from)
        await session.flush()  # free the one-current-price slot before inserting
    new = ProductPrice(
        product_vendor_id=pv.id, price=price, effective_from=start, source=source, reason=reason
    )
    session.add(new)
    await session.flush()
    await session.refresh(pv, ["prices"])
    audit(
        session,
        "product_vendor",
        pv.id,
        "price_change",
        field="price",
        old=old_value,
        new=price,
        reason=reason,
    )
    return new
