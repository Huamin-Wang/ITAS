"""信息

Revision ID: 10c7ec1d9842
Revises: 754a5a5cdfeb
Create Date: 2025-03-22 11:18:18.523120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10c7ec1d9842'
down_revision = '754a5a5cdfeb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course_students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('finally_score', sa.Float(), server_default='0', nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course_students', schema=None) as batch_op:
        batch_op.drop_column('finally_score')

    # ### end Alembic commands ###
