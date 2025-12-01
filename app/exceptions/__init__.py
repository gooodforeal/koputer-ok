"""
Модуль с доменными исключениями
"""

from app.exceptions.base import BaseAppException
from app.exceptions.auth import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenNotFoundError,
    TokenExpiredError,
    TokenAlreadyUsedError,
    FailedToLinkTokenError,
    FailedToSaveTokenError,
    GoogleAuthError,
    TelegramAuthError,
)
from app.exceptions.users import (
    UserNotFoundError,
    UserAlreadyExistsError,
    UserInactiveError,
    InsufficientPermissionsError,
)
from app.exceptions.builds import (
    BuildNotFoundError,
    BuildAccessDeniedError,
    BuildValidationError,
    RatingNotFoundError,
    RatingAlreadyExistsError,
    CommentNotFoundError,
    CommentAccessDeniedError,
    ComponentCategoryError,
)
from app.exceptions.components import (
    ComponentNotFoundError,
    ComponentParseError,
    ComponentParseAlreadyRunningError,
    ComponentParseNotRunningError,
    InvalidComponentCategoryError,
)
from app.exceptions.balance import (
    BalanceNotFoundError,
    InsufficientBalanceError,
    TransactionNotFoundError,
    InvalidTransactionError,
)
from app.exceptions.feedback import (
    FeedbackNotFoundError,
    FeedbackAlreadyExistsError,
    FeedbackAccessDeniedError,
    FeedbackValidationError,
)
from app.exceptions.chat import (
    ChatNotFoundError,
    ChatAccessDeniedError,
    MessageNotFoundError,
    MessageAccessDeniedError,
    ChatAlreadyExistsError,
    InvalidChatStatusError,
)
from app.exceptions.payment import (
    PaymentNotFoundError,
    PaymentCreationError,
    PaymentWebhookError,
    InvalidPaymentDataError,
)

__all__ = [
    "BaseAppException",
    # Auth
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenNotFoundError",
    "TokenExpiredError",
    "TokenAlreadyUsedError",
    "FailedToLinkTokenError",
    "FailedToSaveTokenError",
    "GoogleAuthError",
    "TelegramAuthError",
    # Users
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "UserInactiveError",
    "InsufficientPermissionsError",
    # Builds
    "BuildNotFoundError",
    "BuildAccessDeniedError",
    "BuildValidationError",
    "RatingNotFoundError",
    "RatingAlreadyExistsError",
    "CommentNotFoundError",
    "CommentAccessDeniedError",
    "ComponentCategoryError",
    # Components
    "ComponentNotFoundError",
    "ComponentParseError",
    "ComponentParseAlreadyRunningError",
    "ComponentParseNotRunningError",
    "InvalidComponentCategoryError",
    # Balance
    "BalanceNotFoundError",
    "InsufficientBalanceError",
    "TransactionNotFoundError",
    "InvalidTransactionError",
    # Feedback
    "FeedbackNotFoundError",
    "FeedbackAlreadyExistsError",
    "FeedbackAccessDeniedError",
    "FeedbackValidationError",
    # Chat
    "ChatNotFoundError",
    "ChatAccessDeniedError",
    "MessageNotFoundError",
    "MessageAccessDeniedError",
    "ChatAlreadyExistsError",
    "InvalidChatStatusError",
    # Payment
    "PaymentNotFoundError",
    "PaymentCreationError",
    "PaymentWebhookError",
    "InvalidPaymentDataError",
]
