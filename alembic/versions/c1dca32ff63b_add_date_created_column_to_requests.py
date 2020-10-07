"""Add date_created column to Requests

Revision ID: c1dca32ff63b
Revises: 2b3c372cd0db
Create Date: 2020-10-07 21:38:22.557610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1dca32ff63b'
down_revision = '2b3c372cd0db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('date_created', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('requests', 'date_created')
    # ### end Alembic commands ###
