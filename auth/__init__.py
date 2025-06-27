"""
Sistema de Autenticação Modular - Grupo Vidah
Arquitetura anti-bugs com separação de responsabilidades
"""

from .models import AuthUser, UserSession
from .services import AuthService, UserManagementService
from .decorators import login_required, admin_required, rate_limit
from .validators import AuthValidator
from .security import SecurityManager
from .blueprints import auth_bp

__all__ = [
    'AuthUser',
    'UserSession', 
    'AuthService',
    'UserManagementService',
    'login_required',
    'admin_required',
    'rate_limit',
    'AuthValidator',
    'SecurityManager',
    'auth_bp'
]