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
    get_transaction_repository
)

# Импорты из services
from .services import (
    get_redis_service,
    get_rabbitmq_service,
    get_email_publisher,
    get_auth_token_storage,
    get_auth_service,
    get_build_service,
    get_chat_service,
    get_feedback_service,
    get_user_service,
    get_balance_service,
    get_payment_service,
    get_component_parser_service,
    get_yookassa_service,
    get_shop_parser,
    get_pdf_generator
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
    
    # Services
    "get_redis_service",
    "get_rabbitmq_service",
    "get_email_publisher",
    "get_auth_token_storage",
    "get_auth_service",
    "get_build_service",
    "get_chat_service",
    "get_feedback_service",
    "get_user_service",
    "get_balance_service",
    "get_payment_service",
    "get_component_parser_service",
    "get_yookassa_service",
    "get_shop_parser",
    "get_pdf_generator",
    
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
