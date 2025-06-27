"""
Gerenciador de Configurações do Sistema

Módulo centralizado para gerenciar todas as configurações do sistema
de ecocardiograma de forma segura e organizada.
"""

import os
from typing import Any, Dict, Optional
from .exceptions import SystemException

class ConfigurationManager:
    """Gerenciador centralizado de configurações"""
    
    def __init__(self):
        self._config = {}
        self._load_environment_variables()
    
    def _load_environment_variables(self):
        """Carrega variáveis de ambiente essenciais"""
        self._config.update({
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'SESSION_SECRET': os.environ.get('SESSION_SECRET'),
            'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
            'UPLOAD_FOLDER': os.environ.get('UPLOAD_FOLDER', 'uploads'),
            'MAX_CONTENT_LENGTH': int(os.environ.get('MAX_CONTENT_LENGTH', '16777216')),  # 16MB
            'ALLOWED_EXTENSIONS': {'pdf', 'png', 'jpg', 'jpeg', 'gif'},
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define valor de configuração"""
        self._config[key] = value
    
    def get_database_url(self) -> str:
        """Obtém URL do banco de dados"""
        url = self.get('DATABASE_URL')
        if not url:
            raise SystemException("DATABASE_URL não configurada")
        return url
    
    def get_session_secret(self) -> str:
        """Obtém chave secreta da sessão"""
        secret = self.get('SESSION_SECRET')
        if not secret:
            raise SystemException("SESSION_SECRET não configurada")
        return secret
    
    def is_debug_mode(self) -> bool:
        """Verifica se está em modo debug"""
        return self.get('DEBUG', False)
    
    def get_upload_config(self) -> Dict[str, Any]:
        """Obtém configurações de upload"""
        return {
            'folder': self.get('UPLOAD_FOLDER'),
            'max_size': self.get('MAX_CONTENT_LENGTH'),
            'allowed_extensions': self.get('ALLOWED_EXTENSIONS')
        }

# Instância global do gerenciador
config_manager = ConfigurationManager()