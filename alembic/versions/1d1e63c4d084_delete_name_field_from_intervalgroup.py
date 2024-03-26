"""delete name field from intervalgroup

Revision ID: 1d1e63c4d084
Revises: 5d3333799939
Create Date: 2024-03-26 09:58:49.401732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d1e63c4d084'
down_revision: Union[str, None] = '5d3333799939'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('intervalgroup', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('intervalgroup', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
