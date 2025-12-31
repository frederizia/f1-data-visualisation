import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now_in_utc() -> datetime.datetime:
    """
    Get the current time with UTC timezone information.
    """
    return datetime.datetime.now(datetime.UTC)


class Base(DeclarativeBase):
    # We want all our models to have these fields.
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: _now_in_utc(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: _now_in_utc(),
        onupdate=lambda: _now_in_utc(),
        nullable=False,
    )
