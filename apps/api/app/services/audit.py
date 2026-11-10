from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import AuditLog


def _str(value: Any) -> str | None:
    return None if value is None else str(value)


def audit(
    session: AsyncSession,
    entity: str,
    entity_id: int,
    action: str,
    *,
    field: str | None = None,
    old: Any = None,
    new: Any = None,
    reason: str | None = None,
) -> None:
    """Queue an audit row in the caller's transaction."""
    session.add(
        AuditLog(
            entity=entity,
            entity_id=entity_id,
            action=action,
            field=field,
            old_value=_str(old),
            new_value=_str(new),
            reason=reason,
            actor=get_settings().operator_name,
        )
    )
