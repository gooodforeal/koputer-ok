"""update_builds_structure_with_components

Revision ID: a16054728143
Revises: e7eb35g0g596
Create Date: 2025-10-31 13:25:16.266481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a16054728143'
down_revision = 'e7eb35g0g596'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем новые колонки для компонентов сборки
    op.add_column('builds', sa.Column('cpu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('gpu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('motherboard', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('ram', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('storage', sa.Text(), nullable=True))
    op.add_column('builds', sa.Column('psu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('case', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('cooling', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('additional_info', sa.Text(), nullable=True))
    
    # Удаляем старую колонку content (после миграции данных, если нужно)
    # Сначала делаем её nullable для безопасности
    op.alter_column('builds', 'content', nullable=True)


def downgrade() -> None:
    # Возвращаем обратно
    op.alter_column('builds', 'content', nullable=False)
    
    # Удаляем новые колонки
    op.drop_column('builds', 'additional_info')
    op.drop_column('builds', 'cooling')
    op.drop_column('builds', 'case')
    op.drop_column('builds', 'psu')
    op.drop_column('builds', 'storage')
    op.drop_column('builds', 'ram')
    op.drop_column('builds', 'motherboard')
    op.drop_column('builds', 'gpu')
    op.drop_column('builds', 'cpu')






