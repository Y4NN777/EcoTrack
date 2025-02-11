"""Add waste_type_id to schedules

Revision ID: 27cb3896a267
Revises: 1e549bf2aed8
Create Date: 2025-01-05 21:18:13.138835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27cb3896a267'
down_revision = '1e549bf2aed8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('waste_type_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'waste_types', ['waste_type_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('waste_type_id')

    # ### end Alembic commands ###
