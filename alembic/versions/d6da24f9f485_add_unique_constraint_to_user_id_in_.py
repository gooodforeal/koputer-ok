"""add_unique_constraint_to_user_id_in_feedbacks

Revision ID: d6da24f9f485
Revises: 41e06c1ccd73
Create Date: 2025-10-29 18:14:06.235508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6da24f9f485'
down_revision = '41e06c1ccd73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем уникальный индекс на user_id в таблице feedbacks
    op.create_index('ix_feedbacks_user_id', 'feedbacks', ['user_id'], unique=True)


def downgrade() -> None:
    # Удаляем уникальный индекс при откате миграции
    op.drop_index('ix_feedbacks_user_id', table_name='feedbacks')






