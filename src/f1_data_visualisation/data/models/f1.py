from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Season(Base):
    """
    Model for storing Formula 1 season information.
    """

    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.year} season"
