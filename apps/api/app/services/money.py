"""Line maths. Decimal only; one rounding rule (half-up to the paisa) everywhere."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

PAISA = Decimal("0.01")


def round_money(value: Decimal) -> Decimal:
    return value.quantize(PAISA, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class LineAmounts:
    taxable: Decimal
    gst: Decimal
    total: Decimal


def line_amounts(qty: Decimal, price: Decimal, gst_rate: Decimal) -> LineAmounts:
    taxable = round_money(qty * price)
    gst = round_money(taxable * gst_rate / Decimal(100))
    return LineAmounts(taxable=taxable, gst=gst, total=taxable + gst)
