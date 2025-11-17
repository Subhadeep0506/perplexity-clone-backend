from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class ModelMemory(Base, TimestampMixin):
    """SQLAlchemy model for storing long-term user memory entries extracted from conversations.

    Each entry can represent a durable fact, preference, or contextual note intended to
    personalize future answers. Use selective write logic to avoid cluttering with transient data.
    """

    __tablename__ = "model_memory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    tags: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    if TYPE_CHECKING:
        from .user import User  # pragma: no cover

    user: Mapped["User"] = relationship("User", back_populates="model_memory")

    def __repr__(self) -> str:
        return f"ModelMemory(id={self.id}, user_id={self.user_id}, tags={self.tags}, content={self.content})"
