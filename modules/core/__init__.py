"""
Módulo Core - Funcionalidades essenciais do sistema

Este módulo contém as funcionalidades centrais e base para todos os outros módulos.
"""

from .database import DatabaseManager
from .config import ConfigurationManager
from .validators import DataValidator
from .exceptions import SystemException, ValidationError, DatabaseError

__all__ = [
    'DatabaseManager',
    'ConfigurationManager', 
    'DataValidator',
    'SystemException',
    'ValidationError',
    'DatabaseError'
]