from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

# Serialise money/qty as strings so the browser never sees float rounding.
Dec = Annotated[Decimal, PlainSerializer(lambda v: format(v, "f"), return_type=str)]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Totals(BaseModel):
    taxable: Dec = Decimal("0.00")
    gst: Dec = Decimal("0.00")
    total: Dec = Decimal("0.00")

    def add(self, taxable: Decimal, gst: Decimal, total: Decimal) -> None:
        self.taxable += taxable
        self.gst += gst
        self.total += total
