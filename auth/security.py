"""
Gerenciador de Segurança - Sistema Anti-Bugs
Implementação enterprise com monitoramento avançado
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from flask import request, session, current_app
from utils.logging_system import log_user_action, log_error_with_traceback

class SecurityManager:
    """
    Gerenciador centralizado de segurança
    Implementa padrões enterprise anti-ataques
    """
    
    # Cache para detecção de ataques
    _attack_detection_cache = {}
    _suspicious_ips = set()
    _failed_attempts_cache = {}
    
    @classmethod
    def generate_secure_token(cls, length: int = 32) -> str:
        """
        Gera token criptograficamente seguro
        """
        return secrets.token_urlsafe(length)
    
    @classmethod
    def generate_csrf_token(cls) -> str:
        """
        Gera token CSRF para proteção de formulários
        """
        if 'csrf_token' not in session:
            session['csrf_token'] = cls.generate_secure_token(32)
        return session['csrf_token']
    
    @classmethod
    def validate_csrf_token(cls, token: str) -> bool:
        """
        Valida token CSRF
        """
        session_token = session.get('csrf_token')
        if not session_token or not token:
            return False
        
        # Comparação segura contra timing attacks
        return hmac.compare_digest(session_token, token)
    
    @classmethod
    def hash_sensitive_data(cls, data: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash seguro para dados sensíveis
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        # Usar PBKDF2 para hash mais seguro
        import hashlib
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterações
        )
        
        return hashed.hex(), salt
    
    @classmethod
    def detect_brute_force_attack(cls, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """
        Detecta ataques de força bruta
        """
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        # Limpar tentativas antigas
        if identifier in cls._failed_attempts_cache:
            cls._failed_attempts_cache[identifier] = [
                attempt_time for attempt_time in cls._failed_attempts_cache[identifier]
                if attempt_time > window_start
            ]
        
        # Verificar se excedeu limite
        attempts = len(cls._failed_attempts_cache.get(identifier, []))
        return attempts >= max_attempts
    
    @classmethod
    def register_failed_attempt(cls, identifier: str) -> None:
        """
        Registra tentativa falhada para detecção de ataques
        """
        current_time = time.time()
        
        if identifier not in cls._failed_attempts_cache:
            cls._failed_attempts_cache[identifier] = []
        
        cls._failed_attempts_cache[identifier].append(current_time)
        
        # Verificar se deve marcar como suspeito
        if cls.detect_brute_force_attack(identifier):
            cls._suspicious_ips.add(identifier)
            log_user_action(f'IP suspeito detectado por ataques de força bruta: {identifier}')
    
    @classmethod
    def is_suspicious_ip(cls, ip_address: str) -> bool:
        """
        Verifica se IP está marcado como suspeito
        """
        return ip_address in cls._suspicious_ips
    
    @classmethod
    def detect_sql_injection_attempt(cls, input_string: str) -> bool:
        """
        Detecta tentativas básicas de SQL injection
        """
        if not input_string:
            return False
        
        # Padrões suspeitos básicos
        sql_patterns = [
            r"'.*(?:or|and).*'",
            r"union.*select",
            r"drop.*table",
            r"insert.*into",
            r"delete.*from",
            r"update.*set",
            r"exec.*\(",
            r"script.*>",
            r"<.*script"
        ]
        
        input_lower = input_string.lower()
        
        import re
        for pattern in sql_patterns:
            if re.search(pattern, input_lower):
                return True
        
        return False
    
    @classmethod
    def detect_xss_attempt(cls, input_string: str) -> bool:
        """
        Detecta tentativas básicas de XSS
        """
        if not input_string:
            return False
        
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
            r"<iframe",
            r"<object",
            r"<embed"
        ]
        
        input_lower = input_string.lower()
        
        import re
        for pattern in xss_patterns:
            if re.search(pattern, input_lower):
                return True
        
        return False
    
    @classmethod
    def sanitize_input(cls, input_string: str, max_length: int = 1000) -> str:
        """
        Sanitiza entrada de usuário
        """
        if not input_string:
            return ""
        
        # Truncar se muito longo
        if len(input_string) > max_length:
            input_string = input_string[:max_length]
        
        # Remover caracteres de controle
        import unicodedata
        sanitized = ''.join(
            char for char in input_string 
            if unicodedata.category(char)[0] != 'C' or char in '\n\r\t'
        )
        
        return sanitized.strip()
    
    @classmethod
    def validate_request_integrity(cls, request_obj) -> Tuple[bool, List[str]]:
        """
        Valida integridade geral da requisição
        """
        warnings = []
        
        # Verificar IP suspeito
        ip_address = request_obj.remote_addr
        if cls.is_suspicious_ip(ip_address):
            warnings.append(f"Requisição de IP suspeito: {ip_address}")
        
        # Verificar User-Agent
        user_agent = request_obj.headers.get('User-Agent', '')
        if not user_agent or len(user_agent) < 10:
            warnings.append("User-Agent suspeito ou ausente")
        
        # Verificar Referer em formulários POST
        if request_obj.method == 'POST':
            referer = request_obj.headers.get('Referer', '')
            if not referer:
                warnings.append("Referer ausente em POST")
        
        # Verificar tentativas de injeção nos parâmetros
        for key, value in request_obj.form.items():
            if isinstance(value, str):
                if cls.detect_sql_injection_attempt(value):
                    warnings.append(f"Tentativa de SQL injection no campo '{key}'")
                if cls.detect_xss_attempt(value):
                    warnings.append(f"Tentativa de XSS no campo '{key}'")
        
        # Verificar headers suspeitos
        suspicious_headers = ['X-Forwarded-For', 'X-Real-IP']
        for header in suspicious_headers:
            if header in request_obj.headers:
                value = request_obj.headers[header]
                if not cls._is_valid_ip_list(value):
                    warnings.append(f"Header {header} com formato suspeito")
        
        return len(warnings) == 0, warnings
    
    @classmethod
    def generate_session_fingerprint(cls, request_obj) -> str:
        """
        Gera fingerprint único da sessão
        """
        components = [
            request_obj.remote_addr or 'unknown',
            request_obj.headers.get('User-Agent', 'unknown'),
            request_obj.headers.get('Accept-Language', 'unknown'),
            request_obj.headers.get('Accept-Encoding', 'unknown')
        ]
        
        fingerprint_string = '|'.join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:32]
    
    @classmethod
    def cleanup_security_caches(cls) -> None:
        """
        Limpa caches de segurança (job de manutenção)
        """
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hora
            
            # Limpar tentativas falhadas antigas
            for identifier in list(cls._failed_attempts_cache.keys()):
                cls._failed_attempts_cache[identifier] = [
                    attempt for attempt in cls._failed_attempts_cache[identifier]
                    if attempt > cutoff_time
                ]
                
                if not cls._failed_attempts_cache[identifier]:
                    del cls._failed_attempts_cache[identifier]
            
            # Limpar IPs suspeitos após 24 horas
            cutoff_suspicious = current_time - 86400  # 24 horas
            ips_to_remove = set()
            
            for ip in cls._suspicious_ips:
                # Verificar se ainda tem tentativas recentes
                if ip not in cls._failed_attempts_cache:
                    ips_to_remove.add(ip)
            
            cls._suspicious_ips -= ips_to_remove
            
            log_user_action(f'Limpeza de segurança executada: {len(ips_to_remove)} IPs removidos da lista suspeita')
            
        except Exception as e:
            log_error_with_traceback(f'Erro na limpeza de caches de segurança: {str(e)}')
    
    @staticmethod
    def _is_valid_ip_list(ip_string: str) -> bool:
        """
        Valida lista de IPs em headers
        """
        try:
            import ipaddress
            
            # Separar por vírgula e validar cada IP
            ips = [ip.strip() for ip in ip_string.split(',')]
            
            for ip in ips:
                ipaddress.ip_address(ip)
            
            return True
            
        except ValueError:
            return False

class RequestSecurityMiddleware:
    """
    Middleware de segurança para requisições
    """
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Inicializa middleware na aplicação Flask
        """
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """
        Validações de segurança antes de processar requisição
        """
        try:
            # Validar integridade da requisição
            is_valid, warnings = SecurityManager.validate_request_integrity(request)
            
            if warnings:
                for warning in warnings:
                    log_user_action(f'Alerta de segurança: {warning}', request.remote_addr)
            
            # Bloquear IPs suspeitos em rotas críticas
            if SecurityManager.is_suspicious_ip(request.remote_addr):
                critical_endpoints = ['auth_login', 'criar_usuario', 'editar_usuario']
                if request.endpoint in critical_endpoints:
                    log_user_action(f'Acesso bloqueado para IP suspeito: {request.remote_addr}')
                    from flask import abort
                    abort(403)
            
            # Gerar fingerprint da sessão
            session['fingerprint'] = SecurityManager.generate_session_fingerprint(request)
            
        except Exception as e:
            log_error_with_traceback(f'Erro no middleware de segurança: {str(e)}')
    
    def after_request(self, response):
        """
        Processamento após requisição
        """
        try:
            # Adicionar headers de segurança
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Content Security Policy básico
            csp = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data:;"
            response.headers['Content-Security-Policy'] = csp
            
            return response
            
        except Exception as e:
            log_error_with_traceback(f'Erro no processamento pós-requisição: {str(e)}')
            return response

class AuditLogger:
    """
    Logger de auditoria para eventos de segurança
    """
    
    @staticmethod
    def log_auth_event(event_type: str, user_id: int = None, details: Dict[str, Any] = None):
        """
        Registra eventos de autenticação
        """
        try:
            from flask_login import current_user
            
            audit_data = {
                'event_type': event_type,
                'user_id': user_id or (current_user.id if current_user.is_authenticated else None),
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            log_user_action(f'Evento de auditoria: {event_type}')
            
        except Exception as e:
            log_error_with_traceback(f'Erro no log de auditoria: {str(e)}')
    
    @staticmethod
    def log_security_event(event_type: str, severity: str = 'INFO', details: Dict[str, Any] = None):
        """
        Registra eventos de segurança
        """
        try:
            security_data = {
                'event_type': event_type,
                'severity': severity,
                'ip_address': request.remote_addr if request else None,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            log_user_action(f'Evento de segurança [{severity}]: {event_type}')
            
        except Exception as e:
            log_error_with_traceback(f'Erro no log de segurança: {str(e)}')