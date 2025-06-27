"""
Modelos de Autenticação - Arquitetura Anti-Bugs
Implementação robusta com validações e segurança integrada
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# Timezone de Brasília
BRASILIA_TZ = timezone(timedelta(hours=-3))

def datetime_brasilia():
    """Retorna datetime atual no fuso horário de Brasília"""
    return datetime.now(BRASILIA_TZ)

class AuthUser(UserMixin, db.Model):
    """
    Modelo de usuário com segurança aprimorada
    Implementa padrões anti-vulnerabilidade
    """
    __tablename__ = 'auth_users'
    
    # Campos principais
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    
    # Controle de acesso
    role = Column(String(50), default='user', nullable=False)  # user, admin
    is_active_flag = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Auditoria e segurança
    created_at = Column(DateTime, default=datetime_brasilia, nullable=False)
    updated_at = Column(DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Metadados
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_data = Column(Text)  # JSON para dados extras
    
    # Relacionamentos
    sessions = relationship('UserSession', backref='user', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Construtor personalizado para inicialização adequada"""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password: str) -> None:
        """
        Define senha com hash seguro
        Implementa validação de força
        """
        if not password or len(password) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        
        self.password_hash = generate_password_hash(password)
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def check_password(self, password: str) -> bool:
        """
        Verifica senha com proteção contra ataques
        Implementa rate limiting automático
        """
        if self.is_locked():
            return False
            
        if not password:
            self._register_failed_attempt()
            return False
        
        if check_password_hash(str(self.password_hash), password):
            self._register_successful_login()
            return True
        else:
            self._register_failed_attempt()
            return False
    
    def is_admin(self) -> bool:
        """Verifica se usuário é administrador"""
        return self.role == 'admin'
    
    @property
    def is_active(self) -> bool:
        """Implementação do Flask-Login"""
        return self.is_active_flag and not self.is_locked()
    
    def is_locked(self) -> bool:
        """Verifica se conta está bloqueada"""
        if not self.locked_until:
            return False
        return datetime_brasilia() < self.locked_until
    
    def _register_failed_attempt(self) -> None:
        """Registra tentativa de login falhada"""
        self.failed_login_attempts += 1
        
        # Bloqueia após 5 tentativas por 30 minutos
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime_brasilia() + timedelta(minutes=30)
    
    def _register_successful_login(self) -> None:
        """Registra login bem-sucedido"""
        self.last_login = datetime_brasilia()
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def get_display_name(self) -> str:
        """Retorna nome para exibição"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self, include_sensitive=False) -> dict:
        """Serialização segura para APIs"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'display_name': self.get_display_name(),
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else '-',
            'last_login': self.last_login.strftime('%d/%m/%Y %H:%M') if self.last_login else '-'
        }
        
        if include_sensitive:
            data.update({
                'failed_attempts': self.failed_login_attempts,
                'is_locked': self.is_locked(),
                'locked_until': self.locked_until.isoformat() if self.locked_until else None
            })
        
        return data
    
    def __repr__(self):
        return f'<AuthUser {self.username}>'

class UserSession(db.Model):
    """
    Gerenciamento avançado de sessões
    Controle de segurança e auditoria
    """
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('auth_users.id'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Dados da sessão
    ip_address = Column(String(45))  # Suporta IPv6
    user_agent = Column(Text)
    device_fingerprint = Column(String(255))
    
    # Controle temporal
    created_at = Column(DateTime, default=datetime_brasilia, nullable=False)
    last_activity = Column(DateTime, default=datetime_brasilia, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime)
    revoked_reason = Column(String(100))
    
    def __init__(self, **kwargs):
        """Construtor personalizado para inicialização adequada"""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_valid(self) -> bool:
        """Verifica se sessão é válida"""
        if not self.is_active:
            return False
        
        if self.revoked_at:
            return False
            
        return datetime_brasilia() < self.expires_at
    
    def extend_session(self, hours: int = 24) -> None:
        """Estende validade da sessão"""
        if self.is_valid():
            self.expires_at = datetime_brasilia() + timedelta(hours=hours)
            self.last_activity = datetime_brasilia()
    
    def revoke(self, reason: str = 'manual') -> None:
        """Revoga sessão"""
        self.is_active = False
        self.revoked_at = datetime_brasilia()
        self.revoked_reason = reason
    
    def to_dict(self) -> dict:
        """Serialização para APIs"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<UserSession {self.user_id}:{self.session_token[:8]}...>'