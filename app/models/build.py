from sqlalchemy import Column, String, Text, Integer, ForeignKey, Float, CheckConstraint, Index, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


# Промежуточная таблица для связи многие-ко-многим между Build и Component
build_components = Table(
    'build_components',
    BaseModel.metadata,
    Column('build_id', Integer, ForeignKey('builds.id', ondelete='CASCADE'), primary_key=True),
    Column('component_id', Integer, ForeignKey('components.id', ondelete='CASCADE'), primary_key=True),
    Index('ix_build_components_build_id', 'build_id'),
    Index('ix_build_components_component_id', 'component_id'),
)


class Build(BaseModel):
    """Модель сборки пользователя"""
    __tablename__ = "builds"

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    additional_info = Column(Text, nullable=True)  # Дополнительная информация
    
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    views_count = Column(Integer, default=0, nullable=False)
    
    # Связи
    author = relationship("User", back_populates="builds")
    ratings = relationship("BuildRating", back_populates="build", cascade="all, delete-orphan")
    comments = relationship("BuildComment", back_populates="build", cascade="all, delete-orphan")
    components = relationship("Component", secondary=build_components, lazy="selectin")

    # Индексы для быстрого поиска
    __table_args__ = (
        Index('ix_builds_author_created', 'author_id', 'created_at'),
    )

    @property
    def average_rating(self):
        """Вычисляет средний рейтинг сборки"""
        if not self.ratings:
            return 0.0
        return sum(r.score for r in self.ratings) / len(self.ratings)

    @property
    def ratings_count(self):
        """Возвращает количество оценок"""
        return len(self.ratings) if self.ratings else 0

    @property
    def total_price(self):
        """Вычисляет общую стоимость сборки из суммы цен компонентов"""
        if not self.components:
            return 0.0
        return sum(component.price or 0 for component in self.components)


class BuildRating(BaseModel):
    """Модель оценки сборки"""
    __tablename__ = "build_ratings"

    build_id = Column(Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)  # Оценка от 1 до 5

    # Связи
    build = relationship("Build", back_populates="ratings")
    user = relationship("User", back_populates="build_ratings")

    # Ограничения
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 5', name='check_rating_score'),
        Index('ix_build_ratings_unique', 'build_id', 'user_id', unique=True),
    )


class BuildComment(BaseModel):
    """Модель комментария к сборке"""
    __tablename__ = "build_comments"

    build_id = Column(Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("build_comments.id", ondelete="CASCADE"), nullable=True)  # Для ответов на комментарии

    # Связи
    build = relationship("Build", back_populates="comments")
    user = relationship("User", back_populates="build_comments")
    parent = relationship("BuildComment", remote_side="BuildComment.id", back_populates="replies")
    replies = relationship("BuildComment", back_populates="parent", cascade="all, delete-orphan")

    # Индексы
    __table_args__ = (
        Index('ix_build_comments_build_created', 'build_id', 'created_at'),
    )


class BuildView(BaseModel):
    """Модель для отслеживания просмотров сборок"""
    __tablename__ = "build_views"

    build_id = Column(Integer, ForeignKey("builds.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Связи
    build = relationship("Build")
    user = relationship("User")

    # Уникальный индекс для предотвращения повторных просмотров
    __table_args__ = (
        Index('ix_build_views_unique', 'build_id', 'user_id', unique=True),
    )


