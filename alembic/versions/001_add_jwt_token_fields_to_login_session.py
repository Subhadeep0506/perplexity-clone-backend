"""Add JWT token fields to login_session table

Revision ID: 001
Revises:
Create Date: 2025-11-15 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add JWT token fields to login_session table."""
    # Add new columns for JWT tokens
    op.add_column("login_session", sa.Column("access_token", sa.Text(), nullable=True))
    op.add_column("login_session", sa.Column("refresh_token", sa.Text(), nullable=True))
    op.add_column(
        "login_session", sa.Column("token_expires_at", sa.DateTime(), nullable=True)
    )

    # Create index on access_token for faster lookups
    op.create_index(
        "ix_login_session_access_token", "login_session", ["access_token"], unique=False
    )


def downgrade() -> None:
    """Remove JWT token fields from login_session table."""
    # Drop index
    op.drop_index("ix_login_session_access_token", table_name="login_session")

    # Drop columns
    op.drop_column("login_session", "token_expires_at")
    op.drop_column("login_session", "refresh_token")
    op.drop_column("login_session", "access_token")
