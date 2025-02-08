"""remove_user_id_from_schedules

Revision ID: a2e498e6b250
Revises: 23e498e6b249
Create Date: 2025-01-06 08:47:19.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2e498e6b250'
down_revision = '23e498e6b249'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the foreign key constraint first
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_constraint('fk_schedules_user_id_users', type_='foreignkey')
        batch_op.drop_column('user_id')


def downgrade():
    # Add back the user_id column and foreign key
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_schedules_user_id_users',
            'users',
            ['user_id'],
            ['id']
        )
