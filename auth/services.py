"""
Serviços de Autenticação - Lógica de Negócio
Implementação modular com padrões enterprise
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from flask import request, session
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from app import db
from .models import AuthUser, UserSession, datetime_brasilia
from utils.logging_system import log_user_action, log_error_with_traceback

class AuthService:
    """
    Serviço principal de autenticação
    Implementa padrões de segurança enterprise
    """
    
    @staticmethod
    def authenticate_user(username: str, password: str, ip_address: str = None) -> Tuple[bool, Optional[AuthUser], str]:
        """
        Autentica usuário com validações robustas
        
        Returns:
            Tuple[success, user, message]
        """
        try:
            # Validações básicas
            if not username or not password:
                return False, None, "Credenciais incompletas"
            
            # Buscar usuário
            user = AuthUser.query.filter_by(username=username).first()
            if not user:
                log_user_action(f'Tentativa de login com usuário inexistente: {username}', ip_address)
                return False, None, "Credenciais inválidas"
            
            # Verificar se conta está ativa
            if not user.is_active:
                log_user_action(f'Tentativa de login em conta inativa: {username}', ip_address)
                return False, None, "Conta desativada"
            
            # Verificar senha
            if not user.check_password(password):
                log_user_action(f'Falha na autenticação: {username}', ip_address)
                db.session.commit()  # Salvar tentativas falhadas
                
                if user.is_locked():
                    return False, None, f"Conta bloqueada até {user.locked_until.strftime('%H:%M')}"
                return False, None, "Credenciais inválidas"
            
            # Sucesso na autenticação
            log_user_action(f'Login bem-sucedido: {username}', ip_address)
            db.session.commit()
            
            return True, user, "Autenticação realizada com sucesso"
            
        except Exception as e:
            log_error_with_traceback(f'Erro na autenticação: {str(e)}')
            return False, None, "Erro interno do sistema"
    
    @staticmethod
    def login_user_with_session(user: AuthUser, remember: bool = False) -> bool:
        """
        Efetua login e cria sessão segura
        """
        try:
            # Fazer login com Flask-Login
            login_success = login_user(user, remember=remember)
            
            if login_success:
                # Criar sessão personalizada
                SessionService.create_user_session(
                    user_id=user.id,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')
                )
            
            return login_success
            
        except Exception as e:
            log_error_with_traceback(f'Erro no login de sessão: {str(e)}')
            return False
    
    @staticmethod
    def logout_user_session() -> bool:
        """
        Efetua logout e limpa sessões
        """
        try:
            if current_user.is_authenticated:
                # Revogar sessões ativas
                SessionService.revoke_user_sessions(current_user.id)
                
                # Logout do Flask-Login
                logout_user()
                
                # Limpar sessão Flask
                session.clear()
                
                return True
            
            return False
            
        except Exception as e:
            log_error_with_traceback(f'Erro no logout: {str(e)}')
            return False

class UserManagementService:
    """
    Serviço de gerenciamento de usuários
    CRUD com validações e auditoria
    """
    
    @staticmethod
    def create_user(data: Dict[str, Any]) -> Tuple[bool, Optional[AuthUser], str]:
        """
        Cria novo usuário com validações
        """
        try:
            # Validar dados obrigatórios
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return False, None, f"Campo obrigatório: {field}"
            
            # Validar unicidade
            if AuthUser.query.filter_by(username=data['username']).first():
                return False, None, "Nome de usuário já existe"
            
            if AuthUser.query.filter_by(email=data['email']).first():
                return False, None, "Email já está em uso"
            
            # Criar usuário
            user = AuthUser(
                username=data['username'],
                email=data['email'],
                role=data.get('role', 'user'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                is_verified=data.get('is_verified', False)
            )
            
            # Definir senha
            user.set_password(data['password'])
            
            # Salvar no banco
            db.session.add(user)
            db.session.commit()
            
            log_user_action(f'Usuário criado: {user.username}')
            return True, user, "Usuário criado com sucesso"
            
        except ValueError as e:
            return False, None, str(e)
        except IntegrityError as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro de integridade ao criar usuário: {str(e)}')
            return False, None, "Dados duplicados detectados"
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro ao criar usuário: {str(e)}')
            return False, None, "Erro interno do sistema"
    
    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> Tuple[bool, Optional[AuthUser], str]:
        """
        Atualiza usuário existente
        """
        try:
            user = AuthUser.query.get(user_id)
            if not user:
                return False, None, "Usuário não encontrado"
            
            # Validar unicidade se mudando username/email
            if 'username' in data and data['username'] != user.username:
                if AuthUser.query.filter_by(username=data['username']).first():
                    return False, None, "Nome de usuário já existe"
                user.username = data['username']
            
            if 'email' in data and data['email'] != user.email:
                if AuthUser.query.filter_by(email=data['email']).first():
                    return False, None, "Email já está em uso"
                user.email = data['email']
            
            # Atualizar outros campos
            updatable_fields = ['role', 'first_name', 'last_name', 'is_active_flag', 'is_verified']
            for field in updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            # Atualizar senha se fornecida
            if data.get('password'):
                user.set_password(data['password'])
            
            user.updated_at = datetime_brasilia()
            db.session.commit()
            
            log_user_action(f'Usuário atualizado: {user.username}')
            return True, user, "Usuário atualizado com sucesso"
            
        except ValueError as e:
            return False, None, str(e)
        except IntegrityError as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro de integridade ao atualizar usuário: {str(e)}')
            return False, None, "Dados duplicados detectados"
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro ao atualizar usuário: {str(e)}')
            return False, None, "Erro interno do sistema"
    
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """
        Remove usuário do sistema
        """
        try:
            user = AuthUser.query.get(user_id)
            if not user:
                return False, "Usuário não encontrado"
            
            username = user.username
            
            # Revogar todas as sessões primeiro
            SessionService.revoke_user_sessions(user_id, reason='user_deleted')
            
            # Remover usuário
            db.session.delete(user)
            db.session.commit()
            
            log_user_action(f'Usuário removido: {username}')
            return True, "Usuário removido com sucesso"
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro ao remover usuário: {str(e)}')
            return False, "Erro interno do sistema"
    
    @staticmethod
    def list_users(page: int = 1, per_page: int = 20, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista usuários com paginação e filtros
        """
        try:
            query = AuthUser.query
            
            # Aplicar filtros
            if filters:
                if filters.get('role'):
                    query = query.filter_by(role=filters['role'])
                if filters.get('is_active') is not None:
                    query = query.filter_by(is_active_flag=filters['is_active'])
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        (AuthUser.username.like(search_term)) |
                        (AuthUser.email.like(search_term)) |
                        (AuthUser.first_name.like(search_term)) |
                        (AuthUser.last_name.like(search_term))
                    )
            
            # Ordenar e paginar
            pagination = query.order_by(AuthUser.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'users': [user.to_dict(include_sensitive=True) for user in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            log_error_with_traceback(f'Erro ao listar usuários: {str(e)}')
            return {
                'users': [],
                'total': 0,
                'pages': 0,
                'current_page': 1,
                'per_page': per_page,
                'has_next': False,
                'has_prev': False,
                'error': 'Erro ao carregar usuários'
            }

class SessionService:
    """
    Gerenciamento avançado de sessões
    """
    
    @staticmethod
    def create_user_session(user_id: int, ip_address: str = None, user_agent: str = None) -> Optional[UserSession]:
        """
        Cria nova sessão de usuário
        """
        try:
            # Gerar token único
            session_token = secrets.token_urlsafe(32)
            
            # Criar fingerprint do dispositivo
            device_fingerprint = hashlib.sha256(
                f"{ip_address or 'unknown'}:{user_agent or 'unknown'}".encode()
            ).hexdigest()[:32]
            
            # Criar sessão
            user_session = UserSession(
                user_id=user_id,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                expires_at=datetime_brasilia() + timedelta(hours=24)
            )
            
            db.session.add(user_session)
            db.session.commit()
            
            return user_session
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro ao criar sessão: {str(e)}')
            return None
    
    @staticmethod
    def revoke_user_sessions(user_id: int, reason: str = 'manual') -> int:
        """
        Revoga todas as sessões de um usuário
        """
        try:
            sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
            revoked_count = 0
            
            for session in sessions:
                session.revoke(reason)
                revoked_count += 1
            
            db.session.commit()
            return revoked_count
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro ao revogar sessões: {str(e)}')
            return 0
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Remove sessões expiradas (job de limpeza)
        """
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime_brasilia()
            ).all()
            
            count = len(expired_sessions)
            
            for session in expired_sessions:
                db.session.delete(session)
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(f'Erro na limpeza de sessões: {str(e)}')
            return 0