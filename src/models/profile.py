import base64
from datetime import date
from sqlalchemy import ForeignKey, String, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base, TimestampMixin
from models.enums import FileType


class Profile(Base, TimestampMixin):
    """SQLAlchemy model for the case_records table."""

    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    
    phone: Mapped[str] = mapped_column(String(13), nullable=True)
    email: Mapped[str] = mapped_column(String(40), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)
    date_created: Mapped[date] = mapped_column(Date, nullable=False)
    date_updated: Mapped[date] = mapped_column(Date, nullable=False)

    def __repr__(self) -> str:
        return f"CaseRecord(id={self.id}, file_name={self.file_name}, patient_id={self.patient_id})"
