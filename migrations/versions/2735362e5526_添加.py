"""添加

Revision ID: 2735362e5526
Revises: 
Create Date: 2025-02-08 22:24:57.009272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2735362e5526'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course_students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score', sa.Float(), nullable=True))
        batch_op.alter_column('student_pinyin_name',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('student_grade',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('student_major',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('student_class',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('student_status',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('student_course_method',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course_students', schema=None) as batch_op:
        batch_op.alter_column('student_course_method',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('student_status',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('student_class',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('student_major',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('student_grade',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('student_pinyin_name',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.drop_column('score')

    # ### end Alembic commands ###
