"""add_builds_tables

Revision ID: e7eb35g0g596
Revises: b0c3d4bae7a2
Create Date: 2025-10-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7eb35g0g596'
down_revision = 'b0c3d4bae7a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу builds
    op.create_table('builds',
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('views_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_builds_id'), 'builds', ['id'], unique=False)
    op.create_index(op.f('ix_builds_title'), 'builds', ['title'], unique=False)
    op.create_index('ix_builds_author_created', 'builds', ['author_id', 'created_at'], unique=False)

    # Создаем таблицу build_ratings
    op.create_table('build_ratings',
        sa.Column('build_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('score >= 1 AND score <= 5', name='check_rating_score'),
        sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_build_ratings_id'), 'build_ratings', ['id'], unique=False)
    op.create_index('ix_build_ratings_unique', 'build_ratings', ['build_id', 'user_id'], unique=True)

    # Создаем таблицу build_comments
    op.create_table('build_comments',
        sa.Column('build_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['build_comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_build_comments_id'), 'build_comments', ['id'], unique=False)
    op.create_index('ix_build_comments_build_created', 'build_comments', ['build_id', 'created_at'], unique=False)


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_index('ix_build_comments_build_created', table_name='build_comments')
    op.drop_index(op.f('ix_build_comments_id'), table_name='build_comments')
    op.drop_table('build_comments')
    
    op.drop_index('ix_build_ratings_unique', table_name='build_ratings')
    op.drop_index(op.f('ix_build_ratings_id'), table_name='build_ratings')
    op.drop_table('build_ratings')
    
    op.drop_index('ix_builds_author_created', table_name='builds')
    op.drop_index(op.f('ix_builds_title'), table_name='builds')
    op.drop_index(op.f('ix_builds_id'), table_name='builds')
    op.drop_table('builds')


