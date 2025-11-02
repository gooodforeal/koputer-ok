"""add_telegram_auth_support

Revision ID: b0c3d4bae7a2
Revises: d6da24f9f485
Create Date: 2025-10-29 18:33:09.170246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0c3d4bae7a2'
down_revision = 'd6da24f9f485'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Изменяем nullable для email и google_id (делаем их опциональными)
    op.alter_column('users', 'email',
               existing_type=sa.String(),
               nullable=True)
    op.alter_column('users', 'google_id',
               existing_type=sa.String(),
               nullable=True)
    
    # Добавляем новые поля для Telegram авторизации
    op.add_column('users', sa.Column('telegram_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    
    # Создаем индекс для telegram_id
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)


def downgrade() -> None:
    # Удаляем индекс
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    
    # Удаляем добавленные поля
    op.drop_column('users', 'username')
    op.drop_column('users', 'telegram_id')
    
    # Возвращаем nullable обратно
    op.alter_column('users', 'google_id',
               existing_type=sa.String(),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.String(),
               nullable=False)






