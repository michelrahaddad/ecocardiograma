"""
Validadores de Autenticação - Sistema Anti-Bugs
Validações robustas com padrões enterprise
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from email_validator import validate_email, EmailNotValidError

class AuthValidator:
    """
    Validador centralizado para dados de autenticação
    Implementa padrões de segurança e usabilidade
    """
    
    # Expressões regulares para validação
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    PASSWORD_PATTERNS = {
        'min_length': re.compile(r'.{8,}'),
        'has_uppercase': re.compile(r'[A-Z]'),
        'has_lowercase': re.compile(r'[a-z]'),
        'has_digit': re.compile(r'\d'),
        'has_special': re.compile(r'[!@#$%^&*(),.?":{}|<>]'),
        'no_common': re.compile(r'^(?!.*(password|123456|qwerty|admin)).*$', re.IGNORECASE)
    }
    
    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, List[str]]:
        """
        Valida nome de usuário com regras rigorosas
        
        Returns:
            Tuple[is_valid, errors]
        """
        errors = []
        
        if not username:
            errors.append("Nome de usuário é obrigatório")
            return False, errors
        
        # Normalizar unicode
        username = unicodedata.normalize('NFKC', username.strip())
        
        # Verificar comprimento
        if len(username) < 3:
            errors.append("Nome de usuário deve ter pelo menos 3 caracteres")
        elif len(username) > 30:
            errors.append("Nome de usuário deve ter no máximo 30 caracteres")
        
        # Verificar padrão
        if not cls.USERNAME_PATTERN.match(username):
            errors.append("Nome de usuário deve conter apenas letras, números, _ e -")
        
        # Verificar se não começa ou termina com caracteres especiais
        if username.startswith(('-', '_')) or username.endswith(('-', '_')):
            errors.append("Nome de usuário não pode começar ou terminar com - ou _")
        
        # Verificar palavras reservadas
        reserved_words = ['admin', 'root', 'system', 'user', 'test', 'null', 'undefined']
        if username.lower() in reserved_words:
            errors.append("Nome de usuário não pode ser uma palavra reservada")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, List[str]]:
        """
        Valida email com biblioteca especializada
        
        Returns:
            Tuple[is_valid, errors]
        """
        errors = []
        
        if not email:
            errors.append("Email é obrigatório")
            return False, errors
        
        try:
            # Normalizar e validar
            email = unicodedata.normalize('NFKC', email.strip().lower())
            
            # Usar biblioteca de validação
            valid = validate_email(email)
            normalized_email = valid.email
            
            # Verificar se o domínio não está em lista negra
            domain = normalized_email.split('@')[1]
            if cls._is_disposable_email_domain(domain):
                errors.append("Emails temporários não são permitidos")
            
            return len(errors) == 0, errors
            
        except EmailNotValidError as e:
            errors.append(f"Email inválido: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append("Formato de email inválido")
            return False, errors
    
    @classmethod
    def validate_password(cls, password: str, username: str = None) -> Tuple[bool, List[str], Dict[str, bool]]:
        """
        Valida senha com critérios de segurança avançados
        
        Returns:
            Tuple[is_valid, errors, strength_checks]
        """
        errors = []
        strength_checks = {}
        
        if not password:
            errors.append("Senha é obrigatória")
            return False, errors, strength_checks
        
        # Verificar comprimento mínimo
        strength_checks['min_length'] = bool(cls.PASSWORD_PATTERNS['min_length'].search(password))
        if not strength_checks['min_length']:
            errors.append("Senha deve ter pelo menos 8 caracteres")
        
        # Verificar complexidade
        strength_checks['has_uppercase'] = bool(cls.PASSWORD_PATTERNS['has_uppercase'].search(password))
        strength_checks['has_lowercase'] = bool(cls.PASSWORD_PATTERNS['has_lowercase'].search(password))
        strength_checks['has_digit'] = bool(cls.PASSWORD_PATTERNS['has_digit'].search(password))
        strength_checks['has_special'] = bool(cls.PASSWORD_PATTERNS['has_special'].search(password))
        
        # Calcular score de força
        complexity_score = sum([
            strength_checks['has_uppercase'],
            strength_checks['has_lowercase'], 
            strength_checks['has_digit'],
            strength_checks['has_special']
        ])
        
        if complexity_score < 3:
            errors.append("Senha deve conter ao menos 3 tipos: maiúscula, minúscula, número, símbolo")
        
        # Verificar senhas comuns
        strength_checks['no_common'] = bool(cls.PASSWORD_PATTERNS['no_common'].search(password))
        if not strength_checks['no_common']:
            errors.append("Senha muito comum. Escolha uma senha mais segura")
        
        # Verificar se não contém o username
        if username and username.lower() in password.lower():
            errors.append("Senha não pode conter o nome de usuário")
        
        # Verificar repetições excessivas
        if cls._has_excessive_repetition(password):
            errors.append("Senha não pode ter muitos caracteres repetidos")
        
        # Verificar sequências
        if cls._has_sequential_chars(password):
            errors.append("Senha não pode conter sequências óbvias (123, abc, etc)")
        
        strength_checks['overall_strong'] = len(errors) == 0 and complexity_score >= 3
        
        return len(errors) == 0, errors, strength_checks
    
    @classmethod
    def validate_name(cls, name: str, field_name: str = "Nome") -> Tuple[bool, List[str]]:
        """
        Valida nome próprio
        """
        errors = []
        
        if not name:
            return True, errors  # Nome é opcional
        
        name = unicodedata.normalize('NFKC', name.strip())
        
        # Verificar comprimento
        if len(name) > 100:
            errors.append(f"{field_name} deve ter no máximo 100 caracteres")
        
        # Verificar caracteres válidos (letras, espaços, acentos, hífens)
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name):
            errors.append(f"{field_name} deve conter apenas letras, espaços e hífens")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_role(cls, role: str) -> Tuple[bool, List[str]]:
        """
        Valida função do usuário
        """
        errors = []
        valid_roles = ['user', 'admin']
        
        if not role:
            errors.append("Função é obrigatória")
        elif role not in valid_roles:
            errors.append(f"Função deve ser uma das: {', '.join(valid_roles)}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_user_data(cls, data: Dict[str, any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Valida todos os dados de usuário de uma vez
        
        Returns:
            Tuple[is_valid, field_errors]
        """
        field_errors = {}
        
        # Validar username
        if 'username' in data:
            is_valid, errors = cls.validate_username(data['username'])
            if errors:
                field_errors['username'] = errors
        
        # Validar email
        if 'email' in data:
            is_valid, errors = cls.validate_email(data['email'])
            if errors:
                field_errors['email'] = errors
        
        # Validar senha
        if 'password' in data:
            is_valid, errors, _ = cls.validate_password(
                data['password'], 
                data.get('username')
            )
            if errors:
                field_errors['password'] = errors
        
        # Validar nomes
        if 'first_name' in data:
            is_valid, errors = cls.validate_name(data['first_name'], "Primeiro nome")
            if errors:
                field_errors['first_name'] = errors
        
        if 'last_name' in data:
            is_valid, errors = cls.validate_name(data['last_name'], "Sobrenome")
            if errors:
                field_errors['last_name'] = errors
        
        # Validar função
        if 'role' in data:
            is_valid, errors = cls.validate_role(data['role'])
            if errors:
                field_errors['role'] = errors
        
        return len(field_errors) == 0, field_errors
    
    @staticmethod
    def _is_disposable_email_domain(domain: str) -> bool:
        """
        Verifica se é um domínio de email temporário
        """
        # Lista básica de domínios temporários conhecidos
        disposable_domains = {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email', 'temp-mail.org',
            'yopmail.com', 'maildrop.cc', 'sharklasers.com'
        }
        
        return domain.lower() in disposable_domains
    
    @staticmethod
    def _has_excessive_repetition(password: str) -> bool:
        """
        Verifica se senha tem muitos caracteres repetidos
        """
        if len(password) < 4:
            return False
        
        # Verificar se mais de 50% são do mesmo caractere
        char_counts = {}
        for char in password:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        max_count = max(char_counts.values())
        return max_count > len(password) * 0.5
    
    @staticmethod
    def _has_sequential_chars(password: str) -> bool:
        """
        Verifica sequências óbvias na senha
        """
        sequences = [
            '123456789', 'abcdefghijklmnopqrstuvwxyz', 
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        ]
        
        password_lower = password.lower()
        
        for seq in sequences:
            # Verificar sequências de 4+ caracteres
            for i in range(len(seq) - 3):
                if seq[i:i+4] in password_lower:
                    return True
                # Verificar sequência reversa
                if seq[i:i+4][::-1] in password_lower:
                    return True
        
        return False

class SecurityValidator:
    """
    Validações específicas de segurança
    """
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Valida formato de endereço IP
        """
        if not ip:
            return False
        
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_suspicious_user_agent(user_agent: str) -> bool:
        """
        Detecta user agents suspeitos
        """
        if not user_agent:
            return True
        
        suspicious_patterns = [
            r'bot', r'crawler', r'spider', r'scraper',
            r'curl', r'wget', r'python-requests'
        ]
        
        user_agent_lower = user_agent.lower()
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent_lower):
                return True
        
        return False
    
    @staticmethod
    def validate_session_data(data: Dict[str, any]) -> Tuple[bool, List[str]]:
        """
        Valida dados de sessão
        """
        errors = []
        
        # Verificar IP
        if 'ip_address' in data:
            if not SecurityValidator.validate_ip_address(data['ip_address']):
                errors.append("Endereço IP inválido")
        
        # Verificar User Agent
        if 'user_agent' in data:
            if SecurityValidator.is_suspicious_user_agent(data['user_agent']):
                errors.append("User Agent suspeito detectado")
        
        return len(errors) == 0, errors