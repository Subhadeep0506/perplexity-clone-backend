from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class UserServiceCredential(Base, TimestampMixin):
    __tablename__ = "user_service_credential"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_settings_id: Mapped[int] = mapped_column(
        ForeignKey("user_settings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service_catalog.id", ondelete="CASCADE"), nullable=False, index=True
    )
    api_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    if TYPE_CHECKING:
        from .user import User  # pragma: no cover
        from .user_settings import UserSettings  # pragma: no cover
        from .service_catalog import ServiceCatalog  # pragma: no cover

    user = relationship("User", back_populates="service_credentials")
    settings = relationship("UserSettings", back_populates="service_credentials")
    service = relationship("ServiceCatalog", back_populates="credentials")

    def __repr__(self) -> str:
        return f"UserServiceCredential(id={self.id}, user_id={self.user_id}, service_id={self.service_id})"
