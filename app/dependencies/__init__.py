"""
Пакет зависимостей FastAPI

Этот пакет содержит все зависимости, организованные по логическим группам:
- database: зависимости для работы с базой данных
- repositories: зависимости для репозиториев
- auth: зависимости для аутентификации
- roles: зависимости для проверки ролей
"""

# Импорты из database
from .database import get_db_session

# Импорты из repositories
from .repositories import (
    get_user_repository,
    get_chat_repository,
    get_feedback_repository,
    get_build_repository,
    get_component_repository,
    get_balance_repository,
    get_transaction_repository,
    get_payment_service
)

# Импорты из auth
from .auth import get_current_user, security

# Импорты из roles
from .roles import (
    require_role,
    require_any_role,
    require_admin,
    require_super_admin,
    require_admin_or_super_admin
)

# Экспорт всех зависимостей
__all__ = [
    # Database
    "get_db_session",
    
    # Repositories
    "get_user_repository",
    "get_chat_repository",
    "get_feedback_repository",
    "get_build_repository",
    "get_component_repository",
    "get_balance_repository",
    "get_transaction_repository",
    "get_payment_service",
    
    # Auth
    "get_current_user",
    "security",
    
    # Roles
    "require_role",
    "require_any_role",
    "require_admin",
    "require_super_admin",
    "require_admin_or_super_admin",
]
