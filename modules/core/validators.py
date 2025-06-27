"""
Validadores de dados do sistema

Módulo centralizado para validação de dados de entrada,
garantindo integridade e consistência em todo o sistema.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from .exceptions import ValidationError

class DataValidator:
    """Validador centralizado de dados"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Valida campos obrigatórios"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        if not cpf:
            return False
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Cálculo do primeiro dígito verificador
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = (sum1 * 10) % 11
        if digit1 == 10:
            digit1 = 0
        
        # Cálculo do segundo dígito verificador
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = (sum2 * 10) % 11
        if digit2 == 10:
            digit2 = 0
        
        return cpf[-2:] == f"{digit1}{digit2}"
    
    @staticmethod
    def validate_date(date_str: str, format_str: str = "%d/%m/%Y") -> bool:
        """Valida formato de data"""
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_age(birth_date: str, format_str: str = "%d/%m/%Y") -> int:
        """Calcula e valida idade"""
        try:
            birth = datetime.strptime(birth_date, format_str)
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            
            if age < 0 or age > 150:
                raise ValidationError("Idade inválida")
            
            return age
        except ValueError:
            raise ValidationError("Data de nascimento inválida")
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: float = None, max_val: float = None, field_name: str = "Campo") -> float:
        """Valida valor numérico dentro de um range"""
        try:
            num_value = float(value) if value is not None else None
            
            if num_value is None:
                return None
            
            if min_val is not None and num_value < min_val:
                raise ValidationError(f"{field_name} deve ser maior que {min_val}")
            
            if max_val is not None and num_value > max_val:
                raise ValidationError(f"{field_name} deve ser menor que {max_val}")
            
            return num_value
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} deve ser um número válido")
    
    @staticmethod
    def validate_crm(crm: str) -> bool:
        """Valida formato do CRM"""
        if not crm:
            return False
        
        # Formato: números seguidos de /UF (ex: 12345/SP)
        pattern = r'^\d{4,6}/[A-Z]{2}$'
        return bool(re.match(pattern, crm.upper()))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """Sanitiza string removendo caracteres perigosos"""
        if not value:
            return ""
        
        # Remove caracteres de controle e sanitiza
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value).strip())
        
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados completos do paciente"""
        # Campos obrigatórios
        required_fields = ['nome_paciente', 'data_nascimento', 'sexo', 'data_exame']
        DataValidator.validate_required_fields(data, required_fields)
        
        # Validações específicas
        if not DataValidator.validate_date(data['data_nascimento']):
            raise ValidationError("Data de nascimento inválida")
        
        if not DataValidator.validate_date(data['data_exame']):
            raise ValidationError("Data do exame inválida")
        
        # Calcula idade
        idade = DataValidator.validate_age(data['data_nascimento'])
        
        # Sanitiza dados
        validated_data = {
            'nome_paciente': DataValidator.sanitize_string(data['nome_paciente'], 200),
            'data_nascimento': data['data_nascimento'],
            'idade': idade,
            'sexo': DataValidator.sanitize_string(data['sexo'], 10),
            'data_exame': data['data_exame'],
            'tipo_atendimento': DataValidator.sanitize_string(data.get('tipo_atendimento', ''), 50),
            'medico_usuario': DataValidator.sanitize_string(data.get('medico_usuario', ''), 200),
            'medico_solicitante': DataValidator.sanitize_string(data.get('medico_solicitante', ''), 200),
            'indicacao': DataValidator.sanitize_string(data.get('indicacao', ''), 1000)
        }
        
        return validated_data