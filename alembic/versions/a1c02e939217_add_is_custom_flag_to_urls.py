"""add is_custom flag to urls

Revision ID: a1c02e939217
Revises: e0ea782f5e61
Create Date: 2026-09-03 09:34:36.947668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123newmerge'
down_revision: Union[str, Sequence[str], None] = 'e0ea782f5e61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'urls',
        sa.Column('is_custom', sa.Boolean(), server_default=sa.text('false'), nullable=False)
    )

def downgrade() -> None:
    op.drop_column('urls', 'is_custom')