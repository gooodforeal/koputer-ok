"""
Зависимости для сервисов
"""
from fastapi import Depends
from app.services.redis_service import RedisService
from app.services.rabbitmq_service import RabbitMQService
from app.services.email_publisher import EmailPublisher
from app.services.auth_tokens import AuthTokenStorage
from app.services.auth_service import AuthService
from app.services.build_service import BuildService
from app.services.chat_service import ChatService
from app.services.feedback_service import FeedbackService
from app.services.user_service import UserService
from app.services.balance_service import BalanceService
from app.services.payment_service import PaymentService
from app.services.component_parser import ComponentParserService
from app.services.yookassa_service import YooKassaService
from app.services.shop_parser import ShopParser
from app.services.pdf_generator import PDFGenerator
from .repositories import (
    get_user_repository,
    get_build_repository,
    get_chat_repository,
    get_feedback_repository,
    get_balance_repository,
    get_transaction_repository
)
from app.repositories import (
    UserRepository,
    BuildRepository,
    ChatRepository,
    FeedbackRepository,
    BalanceRepository,
    TransactionRepository
)

__all__ = [
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
    "get_pdf_generator"
]


# Singleton экземпляры для сервисов, которые должны быть глобальными
_redis_service: RedisService | None = None
_rabbitmq_service: RabbitMQService | None = None


def get_redis_service() -> RedisService:
    """
    Получить экземпляр RedisService (singleton)
    
    Returns:
        RedisService: Экземпляр сервиса Redis
    """
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service


def get_rabbitmq_service() -> RabbitMQService:
    """
    Получить экземпляр RabbitMQService (singleton)
    
    Returns:
        RabbitMQService: Экземпляр сервиса RabbitMQ
    """
    global _rabbitmq_service
    if _rabbitmq_service is None:
        _rabbitmq_service = RabbitMQService()
    return _rabbitmq_service


def get_email_publisher(
    rabbitmq_service: RabbitMQService = Depends(get_rabbitmq_service)
) -> EmailPublisher:
    """
    Получить экземпляр EmailPublisher
    
    Args:
        rabbitmq_service: Сервис RabbitMQ
        
    Returns:
        EmailPublisher: Экземпляр publisher для email
    """
    return EmailPublisher(rabbitmq_service)


def get_auth_token_storage(
    redis_service: RedisService = Depends(get_redis_service)
) -> AuthTokenStorage:
    """
    Получить экземпляр AuthTokenStorage
    
    Args:
        redis_service: Сервис Redis
        
    Returns:
        AuthTokenStorage: Экземпляр хранилища токенов
    """
    return AuthTokenStorage(redis_service)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_token_storage: AuthTokenStorage = Depends(get_auth_token_storage),
    email_publisher: EmailPublisher = Depends(get_email_publisher)
) -> AuthService:
    """
    Получить экземпляр AuthService
    
    Args:
        user_repo: Репозиторий пользователей
        auth_token_storage: Хранилище токенов авторизации
        email_publisher: Publisher для отправки email
        
    Returns:
        AuthService: Экземпляр сервиса авторизации
    """
    return AuthService(user_repo, auth_token_storage, email_publisher)


def get_pdf_generator() -> PDFGenerator:
    """
    Получить экземпляр PDFGenerator
    
    Returns:
        PDFGenerator: Экземпляр генератора PDF
    """
    return PDFGenerator()


def get_build_service(
    build_repo: BuildRepository = Depends(get_build_repository),
    redis_service: RedisService = Depends(get_redis_service),
    pdf_generator: PDFGenerator = Depends(get_pdf_generator)
) -> BuildService:
    """
    Получить экземпляр BuildService
    
    Args:
        build_repo: Репозиторий сборок
        redis_service: Сервис Redis
        pdf_generator: Генератор PDF
        
    Returns:
        BuildService: Экземпляр сервиса сборок
    """
    return BuildService(build_repo, redis_service, pdf_generator)


def get_chat_service(
    chat_repo: ChatRepository = Depends(get_chat_repository)
) -> ChatService:
    """
    Получить экземпляр ChatService
    
    Args:
        chat_repo: Репозиторий чатов
        
    Returns:
        ChatService: Экземпляр сервиса чатов
    """
    return ChatService(chat_repo)


def get_feedback_service(
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
) -> FeedbackService:
    """
    Получить экземпляр FeedbackService
    
    Args:
        feedback_repo: Репозиторий отзывов
        
    Returns:
        FeedbackService: Экземпляр сервиса отзывов
    """
    return FeedbackService(feedback_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """
    Получить экземпляр UserService
    
    Args:
        user_repo: Репозиторий пользователей
        
    Returns:
        UserService: Экземпляр сервиса пользователей
    """
    return UserService(user_repo)


def get_balance_service(
    balance_repo: BalanceRepository = Depends(get_balance_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
) -> BalanceService:
    """
    Получить экземпляр BalanceService
    
    Args:
        balance_repo: Репозиторий балансов
        transaction_repo: Репозиторий транзакций
        
    Returns:
        BalanceService: Экземпляр сервиса баланса
    """
    return BalanceService(balance_repo, transaction_repo)


def get_yookassa_service() -> type[YooKassaService]:
    """
    Получить класс YooKassaService
    
    Returns:
        type[YooKassaService]: Класс сервиса Юкассы (все методы статические)
    """
    return YooKassaService


def get_payment_service(
    balance_repo: BalanceRepository = Depends(get_balance_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    email_publisher: EmailPublisher = Depends(get_email_publisher),
    yookassa_service: type[YooKassaService] = Depends(get_yookassa_service)
) -> PaymentService:
    """
    Получить экземпляр PaymentService
    
    Args:
        balance_repo: Репозиторий балансов
        transaction_repo: Репозиторий транзакций
        user_repo: Репозиторий пользователей
        email_publisher: Publisher для отправки email
        yookassa_service: Класс сервиса Юкассы
        
    Returns:
        PaymentService: Экземпляр сервиса платежей
    """
    return PaymentService(balance_repo, transaction_repo, user_repo, email_publisher, yookassa_service)


def get_shop_parser() -> ShopParser:
    """
    Получить экземпляр ShopParser
    
    Returns:
        ShopParser: Экземпляр парсера магазина
    """
    return ShopParser(use_cache=True)


def get_component_parser_service(
    redis_service: RedisService = Depends(get_redis_service),
    shop_parser: ShopParser = Depends(get_shop_parser)
) -> ComponentParserService:
    """
    Получить экземпляр ComponentParserService
    
    Args:
        redis_service: Сервис Redis
        shop_parser: Парсер магазина
        
    Returns:
        ComponentParserService: Экземпляр сервиса парсинга компонентов
    """
    return ComponentParserService(redis_service, shop_parser)
