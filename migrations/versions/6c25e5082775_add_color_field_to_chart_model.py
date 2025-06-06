"""Add color field to Chart model

Revision ID: 6c25e5082775
Revises: f7f20f26b1ba
Create Date: 2025-05-15 00:35:35.413943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c25e5082775'
down_revision = 'f7f20f26b1ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('charts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('charts', schema=None) as batch_op:
        batch_op.drop_column('color')

    # ### end Alembic commands ###
