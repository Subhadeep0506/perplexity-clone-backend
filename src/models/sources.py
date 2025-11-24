from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class Source(Base, TimestampMixin):
    __tablename__ = "source"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer_id: Mapped[int] = mapped_column(
        ForeignKey("answer.id"), nullable=False, index=True
    )
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    if TYPE_CHECKING:
        from .answer import Answer  # pragma: no cover

    answer: Mapped["Answer"] = relationship("Answer", back_populates="sources")

    def __repr__(self) -> str:
        return f"Source(id={self.id}, answer_id={self.answer_id}, source_url={self.source_url})"
