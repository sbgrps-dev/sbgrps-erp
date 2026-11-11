import re
from datetime import date

from fastapi import HTTPException

_MONTH = re.compile(r"^(\d{4})-(\d{2})$")


def parse_month(value: str) -> date:
    """'2026-11' -> date(2026, 11, 1)."""
    m = _MONTH.match(value)
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise HTTPException(422, f"Month must look like 2026-11, got {value!r}")
    return date(int(m.group(1)), int(m.group(2)), 1)


def format_month(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"
