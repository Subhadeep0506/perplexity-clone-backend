from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.database import Base, TimestampMixin


class ServiceCatalog(Base, TimestampMixin):
    __tablename__ = "service_catalog"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(80), nullable=False, unique=True, index=True
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(60), nullable=False)
    default_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )

    if TYPE_CHECKING:
        from .user_service_credential import UserServiceCredential  # pragma: no cover

    credentials = relationship(
        "UserServiceCredential", back_populates="service", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"ServiceCatalog(id={self.id}, name={self.name}, category={self.category}, provider={self.provider})"
