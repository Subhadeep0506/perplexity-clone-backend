from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin
from .sources import Source


class Answer(Base, TimestampMixin):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query_id: Mapped[int] = mapped_column(
        ForeignKey("query.id"), nullable=False, index=True
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    if TYPE_CHECKING:
        from .query import Query  # pragma: no cover

    query: Mapped["Query"] = relationship("Query", back_populates="answers")
    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="answer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Answer(id={self.id}, query_id={self.query_id}, model_used={self.model_used})"
