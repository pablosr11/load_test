"""Add requests table

Revision ID: a675c3302149
Revises: 
Create Date: 2020-10-08 17:15:55.980266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a675c3302149'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('origin_ip', sa.String(), nullable=True),
    sa.Column('origin_port', sa.Integer(), nullable=True),
    sa.Column('endpoint', sa.String(), nullable=True),
    sa.Column('method', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('replies_to', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['replies_to'], ['requests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_endpoint'), 'requests', ['endpoint'], unique=False)
    op.create_index(op.f('ix_requests_id'), 'requests', ['id'], unique=False)
    op.create_index(op.f('ix_requests_method'), 'requests', ['method'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_requests_method'), table_name='requests')
    op.drop_index(op.f('ix_requests_id'), table_name='requests')
    op.drop_index(op.f('ix_requests_endpoint'), table_name='requests')
    op.drop_table('requests')
    # ### end Alembic commands ###