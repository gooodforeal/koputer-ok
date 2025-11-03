"""add_balance_and_transactions_tables

Revision ID: 88b331115fb1
Revises: 28fdcbf54233
Create Date: 2025-11-03 20:59:01.346928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88b331115fb1'
down_revision = '28fdcbf54233'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем enum типы для транзакций (с проверкой через SQL)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transactiontype AS ENUM ('DEPOSIT', 'WITHDRAWAL', 'PAYMENT', 'REFUND');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transactionstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаем таблицу balances
    op.create_table('balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_balances_user_id'), 'balances', ['user_id'], unique=False)
    
    # Создаем таблицу transactions с inline enum (чтобы не создавать тип заново)
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('balance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('transaction_type', sa.dialects.postgresql.ENUM('DEPOSIT', 'WITHDRAWAL', 'PAYMENT', 'REFUND', name='transactiontype', create_type=False), nullable=False),
        sa.Column('status', sa.dialects.postgresql.ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED', name='transactionstatus', create_type=False), nullable=False),
        sa.Column('payment_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['balance_id'], ['balances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_balance_id'), 'transactions', ['balance_id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_status'), 'transactions', ['status'], unique=False)
    op.create_index(op.f('ix_transactions_type'), 'transactions', ['transaction_type'], unique=False)
    op.create_index(op.f('ix_transactions_payment_id'), 'transactions', ['payment_id'], unique=True)
    op.create_index(op.f('ix_transactions_user_created'), 'transactions', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index(op.f('ix_transactions_user_created'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_payment_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_status'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_balance_id'), table_name='transactions')
    
    # Удаляем таблицы
    op.drop_table('transactions')
    op.drop_index(op.f('ix_balances_user_id'), table_name='balances')
    op.drop_table('balances')
    
    # Удаляем enum типы
    transaction_status_enum = sa.Enum(name='transactionstatus')
    transaction_status_enum.drop(op.get_bind(), checkfirst=True)
    
    transaction_type_enum = sa.Enum(name='transactiontype')
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)






