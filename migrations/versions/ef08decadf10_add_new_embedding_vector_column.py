"""Add new embedding_vector column

Revision ID: ef08decadf10
Revises: 46a42c9e6df1
Create Date: 2024-07-29 12:08:31.388085

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'ef08decadf10'
down_revision = '46a42c9e6df1'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new embedding_vector column
    op.add_column('optimized_opportunity', sa.Column('new_embedding_vector', sa.ARRAY(sa.Float), nullable=True))


def downgrade():
    # Remove the new embedding_vector column
    op.drop_column('optimized_opportunity', 'new_embedding_vector')
