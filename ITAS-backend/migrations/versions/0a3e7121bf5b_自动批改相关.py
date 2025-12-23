"""自动批改相关

Revision ID: 0a3e7121bf5b
Revises: 282d6276435c
Create Date: 2025-12-18 23:42:28.990156
"""

from alembic import op
import sqlalchemy as sa


revision = '0a3e7121bf5b'
down_revision = '282d6276435c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 创建自动批改结果表
    op.create_table(
        'grading_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assignment_id', sa.Integer(), nullable=True),
        sa.Column('quiz_id', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.Integer(), nullable=True),
        sa.Column('student_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('student_answer', sa.Text(), nullable=True),
        sa.Column('reference_answer', sa.Text(), nullable=True),
        sa.Column('total_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('score', sa.Numeric(5, 2), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('grading_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
    )

    # 2. 修改 quiz_response：student_id → student_number
    with op.batch_alter_table('quiz_response', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('student_number', sa.Text(), nullable=False)
        )
        # ⚠️ SQLite 下不要 drop_constraint
        batch_op.drop_column('student_id')


def downgrade():
    # 回滚 quiz_response
    with op.batch_alter_table('quiz_response', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('student_id', sa.Integer(), nullable=False)
        )
        # 给外键显式命名，避免再次生成 None
        batch_op.create_foreign_key(
            'fk_quiz_response_student',
            'user',
            ['student_id'],
            ['id']
        )
        batch_op.drop_column('student_number')

    # 删除自动批改结果表
    op.drop_table('grading_results')
