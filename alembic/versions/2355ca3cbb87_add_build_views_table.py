"""add_build_views_table

Revision ID: 2355ca3cbb87
Revises: a16054728143
Create Date: 2025-10-31 13:37:06.976317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2355ca3cbb87'
down_revision = 'a16054728143'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы build_views для отслеживания просмотров
    op.create_table(
        'build_views',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('build_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание уникального индекса для предотвращения повторных просмотров
    op.create_index(
        'ix_build_views_unique',
        'build_views',
        ['build_id', 'user_id'],
        unique=True
    )


def downgrade() -> None:
    # Удаление индекса
    op.drop_index('ix_build_views_unique', table_name='build_views')
    
    # Удаление таблицы
    op.drop_table('build_views')






