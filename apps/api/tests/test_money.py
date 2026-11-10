from decimal import Decimal as D

import pytest

from app.services.money import line_amounts
from app.services.prices import normalise


@pytest.mark.parametrize(
    ("qty", "price", "rate", "taxable", "gst", "total"),
    [
        # Rows from the Nov-26 file
        ("100", "75.68", "18", "7568.00", "1362.24", "8930.24"),
        ("40", "89.61", "18", "3584.40", "645.19", "4229.59"),
        ("50", "103.54", "18", "5177.00", "931.86", "6108.86"),
        ("24", "30.00", "5", "720.00", "36.00", "756.00"),
        ("13", "95.00", "5", "1235.00", "61.75", "1296.75"),
        ("72", "18.00", "18", "1296.00", "233.28", "1529.28"),
        # Fractional quantity, half-up rounding
        ("2.5", "33.33", "18", "83.33", "15.00", "98.33"),
    ],
)
def test_line_amounts_match_source_file(qty, price, rate, taxable, gst, total):
    a = line_amounts(D(qty), D(price), D(rate))
    assert (a.taxable, a.gst, a.total) == (D(taxable), D(gst), D(total))


def test_search_normalise_matches_alias_spellings():
    keys = {normalise(s) for s in ["STERIX-A super", "STERIX A SUPER", "sterix-a  SUPER"]}
    assert keys == {"sterixasuper"}
