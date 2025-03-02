"""fix_schedules_waste_type_column

Revision ID: 23e498e6b249
Revises: 27cb3896a267
Create Date: 2025-01-05 22:30:39.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '23e498e6b249'
down_revision = '27cb3896a267'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    connection = op.get_bind()
    
    # Check if waste_type_id column exists
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('schedules')]
    
    if 'waste_type_id' not in columns:
        # Get or create default waste type
        first_waste_type = connection.execute(text('SELECT id FROM waste_types LIMIT 1')).fetchone()
        default_waste_type_id = first_waste_type[0] if first_waste_type else None
        
        if default_waste_type_id is None:
            connection.execute(
                text("INSERT INTO waste_types (name, description, disposal_method, created_at) VALUES (:name, :desc, :method, CURRENT_TIMESTAMP)"),
                {"name": "General Waste", "desc": "General waste materials", "method": "Standard disposal"}
            )
            default_waste_type_id = connection.execute(text('SELECT id FROM waste_types ORDER BY id DESC LIMIT 1')).fetchone()[0]
        
        # Add the column and set default value
        with op.batch_alter_table('schedules', schema=None) as batch_op:
            batch_op.add_column(sa.Column('waste_type_id', sa.Integer(), nullable=True))
            
        # Update existing records
        connection.execute(
            text('UPDATE schedules SET waste_type_id = :waste_type_id'),
            {"waste_type_id": default_waste_type_id}
        )
        
        # Make it non-nullable and add foreign key
        with op.batch_alter_table('schedules', schema=None) as batch_op:
            batch_op.alter_column('waste_type_id', nullable=False)
            batch_op.create_foreign_key(
                'fk_schedules_waste_type_id_waste_types',
                'waste_types',
                ['waste_type_id'],
                ['id']
            )


def downgrade():
    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_constraint('fk_schedules_waste_type_id_waste_types', type_='foreignkey')
        batch_op.drop_column('waste_type_id')