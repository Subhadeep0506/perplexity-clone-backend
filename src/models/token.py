from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class TokenUsage(Base, TimestampMixin):
    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("session.id"), nullable=True, index=True
    )
    message_id: Mapped[int | None] = mapped_column(
        ForeignKey("message.id"), nullable=True, index=True
    )
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    if TYPE_CHECKING:
        from .user import User  # pragma: no cover
        from .session import Session  # pragma: no cover
        from .message import Message  # pragma: no cover

    user: Mapped["User"] = relationship("User")
    session: Mapped["Session"] = relationship("Session")
    message: Mapped["Message"] = relationship("Message")

    def __repr__(self) -> str:
        return f"TokenUsage(id={self.id}, user_id={self.user_id}, tokens_used={self.tokens_used})"
