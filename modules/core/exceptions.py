"""
Exceções personalizadas do sistema

Definições de exceções customizadas para tratamento de erros específicos
do sistema de ecocardiograma.
"""

class SystemException(Exception):
    """Exceção base para o sistema"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(SystemException):
    """Erro de validação de dados"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")

class DatabaseError(SystemException):
    """Erro de operação no banco de dados"""
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message, "DATABASE_ERROR")

class AuthenticationError(SystemException):
    """Erro de autenticação"""
    def __init__(self, message: str = "Acesso não autorizado"):
        super().__init__(message, "AUTH_ERROR")

class BusinessRuleError(SystemException):
    """Erro de regra de negócio"""
    def __init__(self, message: str, rule: str = None):
        self.rule = rule
        super().__init__(message, "BUSINESS_RULE_ERROR")

class FileProcessingError(SystemException):
    """Erro de processamento de arquivos"""
    def __init__(self, message: str, file_path: str = None):
        self.file_path = file_path
        super().__init__(message, "FILE_PROCESSING_ERROR")