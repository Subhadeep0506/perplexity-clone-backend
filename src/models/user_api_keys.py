from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class UserAPIKeys(Base, TimestampMixin):
    __tablename__ = "user_api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_settings_id: Mapped[int] = mapped_column(
        ForeignKey("user_settings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    # Encrypted API key stored here
    encrypted_api_key: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )

    if TYPE_CHECKING:
        from .user import User  # pragma: no cover
        from .user_settings import UserSettings  # pragma: no cover
        from .user_service_credential import UserServiceCredential  # pragma: no cover

    user = relationship("User", back_populates="api_keys")
    settings = relationship("UserSettings", back_populates="api_keys")
    service_credentials = relationship(
        "UserServiceCredential", back_populates="api_key", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"UserAPIKeys(id={self.id}, user_id={self.user_id}, title={self.title})"
