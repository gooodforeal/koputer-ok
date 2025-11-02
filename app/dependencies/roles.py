"""
Зависимости для проверки ролей пользователей
"""
from fastapi import Depends, HTTPException, status
from typing import List, Union
from app.models.user import User, UserRole
from .auth import get_current_user

# Зависимости для проверки ролей
__all__ = [
    "require_role", 
    "require_any_role", 
    "require_admin", 
    "require_super_admin", 
    "require_admin_or_super_admin"
]


def require_role(required_roles: Union[UserRole, List[UserRole]]):
    """
    Фабрика зависимостей для проверки ролей пользователя.
    
    Args:
        required_roles: Роль или список ролей, которые требуются для доступа
    
    Returns:
        Зависимость, которая проверяет роль пользователя
    """
    if isinstance(required_roles, UserRole):
        required_roles = [required_roles]
    
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Проверяет, что у пользователя есть одна из требуемых ролей"""
        if current_user.role not in required_roles:
            roles_str = " или ".join([role.value for role in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется роль: {roles_str}"
            )
        return current_user
    
    return role_checker


def require_any_role(*roles: UserRole):
    """
    Создает зависимость для проверки любой из переданных ролей.
    
    Args:
        *roles: Роли, любая из которых подходит для доступа
    
    Returns:
        Зависимость для проверки ролей
    """
    return require_role(list(roles))


# Готовые зависимости для часто используемых ролей
require_admin = require_role(UserRole.ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_admin_or_super_admin = require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])
