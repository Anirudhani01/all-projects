"""add image fields to employees

Revision ID: simple_add_image_fields
Revises: 
Create Date: 2025-08-11 09:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'simple_add_image_fields'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add image fields to employees table."""
    # Add new columns for image support
    op.add_column('employees', sa.Column('image_path', sa.String(length=500), nullable=True))
    op.add_column('employees', sa.Column('image_hash', sa.String(length=64), nullable=True))


def downgrade() -> None:
    """Remove image fields from employees table."""
    op.drop_column('employees', 'image_hash')
    op.drop_column('employees', 'image_path')
