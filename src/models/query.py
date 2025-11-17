from datetime import date
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin
from .answer import Answer


class Query(Base, TimestampMixin):
    __tablename__ = "query"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    parent_query_id: Mapped[int | None] = mapped_column(
        ForeignKey("query.id"), nullable=True, index=True
    )

    if TYPE_CHECKING:
        from .session import Session  # pragma: no cover
        from .user import User

    session: Mapped["Session"] = relationship("Session", back_populates="queries")
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="query", cascade="all, delete-orphan"
    )
    parent: Mapped["Query"] = relationship(
        "Query", remote_side=[id], backref="children"
    )

    def __repr__(self) -> str:
        return (
            f"Query(id={self.id}, session_id={self.session_id}, user_id={self.user_id})"
        )
