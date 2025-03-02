"""Add team column to Schedule model

Revision ID: 1e549bf2aed8
Revises: 
Create Date: 2025-01-04 14:20:51.575869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e549bf2aed8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team', sa.String(length=100), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_column('team')

    # ### end Alembic commands ###
