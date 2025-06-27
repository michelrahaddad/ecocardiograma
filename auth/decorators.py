"""
Decoradores de Segurança - Sistema Anti-Bugs
Implementação robusta com rate limiting e auditoria
"""

import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Callable
from flask import request, redirect, url_for, flash, jsonify, session
from flask_login import current_user
from utils.logging_system import log_user_action, log_error_with_traceback

# Cache em memória para rate limiting (em produção usar Redis)
_rate_limit_cache = {}

class AuthDecorators:
    """
    Coleção de decoradores de autenticação e autorização
    """
    
    @staticmethod
    def login_required(f: Callable) -> Callable:
        """
        Decorator modular para exigir login
        Substitui o @login_required do Flask-Login com melhorias
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not current_user.is_authenticated:
                    # Salvar URL de destino para redirecionamento
                    session['next_url'] = request.url
                    
                    # Log da tentativa de acesso não autorizado
                    log_user_action(
                        f'Acesso negado a {request.endpoint} - usuário não autenticado',
                        request.remote_addr
                    )
                    
                    if request.is_json:
                        return jsonify({
                            'error': 'Autenticação necessária',
                            'redirect': url_for('auth_login')
                        }), 401
                    
                    flash('Faça login para acessar esta página.', 'info')
                    return redirect(url_for('auth_login'))
                
                # Verificar se usuário ainda está ativo
                if not current_user.is_active:
                    log_user_action(
                        f'Acesso negado a {request.endpoint} - conta inativa: {current_user.username}',
                        request.remote_addr
                    )
                    
                    if request.is_json:
                        return jsonify({'error': 'Conta desativada'}), 403
                    
                    flash('Sua conta foi desativada. Contate o administrador.', 'error')
                    return redirect(url_for('auth_logout'))
                
                return f(*args, **kwargs)
                
            except Exception as e:
                log_error_with_traceback(f'Erro no decorator login_required: {str(e)}')
                
                if request.is_json:
                    return jsonify({'error': 'Erro interno do sistema'}), 500
                
                flash('Erro de autenticação. Tente novamente.', 'error')
                return redirect(url_for('auth_login'))
        
        return decorated_function
    
    @staticmethod
    def admin_required(f: Callable) -> Callable:
        """
        Decorator para exigir privilégios administrativos
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Primeiro verificar se está logado
                if not current_user.is_authenticated:
                    session['next_url'] = request.url
                    
                    log_user_action(
                        f'Acesso admin negado a {request.endpoint} - não autenticado',
                        request.remote_addr
                    )
                    
                    if request.is_json:
                        return jsonify({'error': 'Autenticação necessária'}), 401
                    
                    flash('Faça login para acessar esta página.', 'info')
                    return redirect(url_for('auth_login'))
                
                # Verificar se é administrador
                if not current_user.is_admin():
                    log_user_action(
                        f'Acesso admin negado a {request.endpoint} - usuário {current_user.username} sem privilégios',
                        request.remote_addr
                    )
                    
                    if request.is_json:
                        return jsonify({'error': 'Privilégios administrativos necessários'}), 403
                    
                    flash('Acesso negado. Privilégios administrativos necessários.', 'error')
                    return redirect(url_for('index'))
                
                return f(*args, **kwargs)
                
            except Exception as e:
                log_error_with_traceback(f'Erro no decorator admin_required: {str(e)}')
                
                if request.is_json:
                    return jsonify({'error': 'Erro interno do sistema'}), 500
                
                flash('Erro de autorização. Tente novamente.', 'error')
                return redirect(url_for('index'))
        
        return decorated_function
    
    @staticmethod
    def rate_limit(max_requests: int = 60, per_seconds: int = 60, by_ip: bool = True):
        """
        Decorator para rate limiting avançado
        
        Args:
            max_requests: Número máximo de requisições
            per_seconds: Período em segundos
            by_ip: Se True, limita por IP; se False, por usuário
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # Determinar chave para rate limiting
                    if by_ip:
                        key = f"ip:{request.remote_addr}:{request.endpoint}"
                    else:
                        if current_user.is_authenticated:
                            key = f"user:{current_user.id}:{request.endpoint}"
                        else:
                            key = f"anon:{request.remote_addr}:{request.endpoint}"
                    
                    current_time = time.time()
                    
                    # Limpar entradas expiradas
                    AuthDecorators._cleanup_rate_limit_cache(current_time)
                    
                    # Verificar limite
                    if key not in _rate_limit_cache:
                        _rate_limit_cache[key] = []
                    
                    # Filtrar requisições dentro da janela de tempo
                    window_start = current_time - per_seconds
                    _rate_limit_cache[key] = [
                        req_time for req_time in _rate_limit_cache[key] 
                        if req_time > window_start
                    ]
                    
                    # Verificar se excedeu o limite
                    if len(_rate_limit_cache[key]) >= max_requests:
                        log_user_action(
                            f'Rate limit excedido para {key} em {request.endpoint}',
                            request.remote_addr
                        )
                        
                        if request.is_json:
                            return jsonify({
                                'error': 'Muitas requisições. Tente novamente em alguns minutos.',
                                'retry_after': per_seconds
                            }), 429
                        
                        flash('Muitas tentativas. Aguarde alguns minutos.', 'warning')
                        return redirect(request.referrer or url_for('index'))
                    
                    # Registrar requisição
                    _rate_limit_cache[key].append(current_time)
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    log_error_with_traceback(f'Erro no rate limiting: {str(e)}')
                    # Em caso de erro, permitir acesso para não quebrar o sistema
                    return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    @staticmethod
    def require_session_validation(f: Callable) -> Callable:
        """
        Decorator para validar integridade da sessão
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if current_user.is_authenticated:
                    # Verificar se sessão ainda é válida
                    user_id = current_user.id
                    ip_address = request.remote_addr
                    
                    # Aqui poderia verificar com SessionService se necessário
                    # Por enquanto, validação básica
                    
                    # Verificar mudança de IP suspeita (opcional)
                    last_ip = session.get('last_ip')
                    if last_ip and last_ip != ip_address:
                        log_user_action(
                            f'Mudança de IP detectada para usuário {current_user.username}: {last_ip} -> {ip_address}',
                            ip_address
                        )
                        # Em ambiente de produção, poderia forçar re-autenticação
                    
                    session['last_ip'] = ip_address
                
                return f(*args, **kwargs)
                
            except Exception as e:
                log_error_with_traceback(f'Erro na validação de sessão: {str(e)}')
                return f(*args, **kwargs)
        
        return decorated_function
    
    @staticmethod
    def _cleanup_rate_limit_cache(current_time: float) -> None:
        """
        Limpa entradas antigas do cache de rate limiting
        """
        try:
            # Remover entradas mais antigas que 1 hora
            cutoff_time = current_time - 3600
            
            keys_to_remove = []
            for key, timestamps in _rate_limit_cache.items():
                # Filtrar timestamps antigos
                _rate_limit_cache[key] = [
                    ts for ts in timestamps if ts > cutoff_time
                ]
                
                # Marcar chaves vazias para remoção
                if not _rate_limit_cache[key]:
                    keys_to_remove.append(key)
            
            # Remover chaves vazias
            for key in keys_to_remove:
                del _rate_limit_cache[key]
                
        except Exception as e:
            log_error_with_traceback(f'Erro na limpeza do cache de rate limiting: {str(e)}')

# Aliases para facilitar importação
login_required = AuthDecorators.login_required
admin_required = AuthDecorators.admin_required
rate_limit = AuthDecorators.rate_limit
require_session_validation = AuthDecorators.require_session_validation