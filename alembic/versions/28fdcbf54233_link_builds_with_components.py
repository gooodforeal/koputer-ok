"""link_builds_with_components

Revision ID: 28fdcbf54233
Revises: 1b66b1474c37
Create Date: 2025-11-01 22:35:44.334250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28fdcbf54233'
down_revision = '1b66b1474c37'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем промежуточную таблицу build_components
    op.create_table(
        'build_components',
        sa.Column('build_id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('build_id', 'component_id')
    )
    
    # Создаем индексы для промежуточной таблицы
    op.create_index('ix_build_components_build_id', 'build_components', ['build_id'])
    op.create_index('ix_build_components_component_id', 'build_components', ['component_id'])
    
    # Удаляем старые колонки компонентов из таблицы builds
    op.drop_column('builds', 'cpu')
    op.drop_column('builds', 'gpu')
    op.drop_column('builds', 'motherboard')
    op.drop_column('builds', 'ram')
    op.drop_column('builds', 'storage')
    op.drop_column('builds', 'psu')
    op.drop_column('builds', 'case')
    op.drop_column('builds', 'cooling')
    
    # Удаляем колонку content, если она существует (из старой миграции)
    # Проверяем существование колонки перед удалением
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('builds')]
    if 'content' in columns:
        op.drop_column('builds', 'content')


def downgrade() -> None:
    # Возвращаем старые колонки компонентов
    op.add_column('builds', sa.Column('cpu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('gpu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('motherboard', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('ram', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('storage', sa.Text(), nullable=True))
    op.add_column('builds', sa.Column('psu', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('case', sa.String(200), nullable=True))
    op.add_column('builds', sa.Column('cooling', sa.String(200), nullable=True))
    
    # Удаляем промежуточную таблицу
    op.drop_index('ix_build_components_component_id', table_name='build_components')
    op.drop_index('ix_build_components_build_id', table_name='build_components')
    op.drop_table('build_components')






