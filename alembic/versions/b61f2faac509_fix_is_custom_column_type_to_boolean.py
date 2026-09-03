"""fix is_custom column type to boolean

Revision ID: b61f2faac509
Revises: 70236a77f1ed
Create Date: 2026-09-03 01:49:46.004136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b61f2faac509'
down_revision: Union[str, Sequence[str], None] = '70236a77f1ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('urls', 'is_custom', server_default=None)
    op.alter_column(
        'urls', 'is_custom',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        postgresql_using='is_custom::boolean',
        existing_nullable=False,
    )
    op.alter_column('urls', 'is_custom', server_default=sa.text('false'))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('urls', 'is_custom', server_default=None)
    op.alter_column(
        'urls', 'is_custom',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        postgresql_using='is_custom::integer',
        existing_nullable=False,
    )
    op.alter_column('urls', 'is_custom', server_default=sa.text('0'))