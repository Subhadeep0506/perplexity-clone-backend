import base64
from datetime import date
from sqlalchemy import ForeignKey, String, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base, TimestampMixin
from models.enums import FileType


class User(Base, TimestampMixin):
    """SQLAlchemy model for the case_records table."""

    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name="ck_patients_email_format",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    
    date_created: Mapped[date] = mapped_column(Date, nullable=False)
    date_updated: Mapped[date] = mapped_column(Date, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, full_name={self.full_name}, email={self.email})"
