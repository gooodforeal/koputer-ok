"""add_components_table

Revision ID: 1b66b1474c37
Revises: 2355ca3cbb87
Create Date: 2025-10-31 21:42:14.141090

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '1b66b1474c37'
down_revision = '2355ca3cbb87'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем enum только если его еще нет (используем IF NOT EXISTS через execute)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE componentcategory AS ENUM (
                'PROCESSORY',
                'MATERINSKIE_PLATY',
                'VIDEOKARTY',
                'OPERATIVNAYA_PAMYAT',
                'KORPUSA',
                'BLOKI_PITANIYA',
                'ZHESTKIE_DISKI',
                'OHLAZHDENIE',
                'SSD_NAKOPITELI'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Создаем enum объект для использования в таблице
    component_category_enum = postgresql.ENUM(
        'PROCESSORY',
        'MATERINSKIE_PLATY',
        'VIDEOKARTY',
        'OPERATIVNAYA_PAMYAT',
        'KORPUSA',
        'BLOKI_PITANIYA',
        'ZHESTKIE_DISKI',
        'OHLAZHDENIE',
        'SSD_NAKOPITELI',
        name='componentcategory',
        create_type=False  # Не создавать тип, так как мы уже создали его выше
    )
    
    # Проверяем, существует ли таблица, и создаем только если не существует
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE components (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                link VARCHAR NOT NULL,
                price INTEGER,
                image TEXT,
                category componentcategory NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE
            );
            
            CREATE INDEX ix_components_id ON components(id);
            CREATE INDEX ix_components_name ON components(name);
            CREATE INDEX ix_components_category ON components(category);
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)


def downgrade() -> None:
    # Проверяем существование таблицы перед удалением
    op.execute("""
        DO $$ BEGIN
            -- Удаляем индексы только если они существуют
            DROP INDEX IF EXISTS ix_components_category;
            DROP INDEX IF EXISTS ix_components_name;
            DROP INDEX IF EXISTS ix_components_id;
            
            -- Удаляем таблицу только если она существует
            DROP TABLE IF EXISTS components;
        EXCEPTION
            WHEN undefined_table THEN null;
            WHEN undefined_object THEN null;
        END $$;
    """)
    
    # Удаляем enum
    op.execute('DROP TYPE IF EXISTS componentcategory')






