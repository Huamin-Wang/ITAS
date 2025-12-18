"""自动批改相关

Revision ID: 591144251239
Revises: 282d6276435c
Create Date: 2025-12-18 23:07:39.789143
"""

from alembic import op
import sqlalchemy as sa

revision = '591144251239'
down_revision = '282d6276435c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('quiz_response', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('student_number', sa.Text(), nullable=False)
        )
        # ⚠️ SQLite 下不要 drop_constraint
        batch_op.drop_column('student_id')


def downgrade():
    with op.batch_alter_table('quiz_response', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('student_id', sa.Integer(), nullable=False)
        )
        # 这里是否需要外键，看你业务是否真的回退
        batch_op.create_foreign_key(
            'fk_quiz_response_student',
            'user',
            ['student_id'],
            ['id']
        )
        batch_op.drop_column('student_number')
