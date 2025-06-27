"""
Serviço de Exames - Lógica de negócio para exames

Centraliza toda a lógica de negócio relacionada aos exames de ecocardiograma,
eliminando duplicação de código e implementando padrões anti-bug.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from models import Exame
from modules.core.database import DatabaseManager
from modules.core.validators import DataValidator
from modules.core.exceptions import ValidationError, DatabaseError, BusinessRuleError

class ExamService:
    """Serviço centralizado para operações de exames"""
    
    @staticmethod
    def create_exam(exam_data: Dict[str, Any]) -> Exame:
        """Cria novo exame com validação completa"""
        try:
            # Validação de dados
            validated_data = DataValidator.validate_patient_data(exam_data)
            
            # Verificação de regras de negócio
            ExamService._validate_business_rules(validated_data)
            
            # Criação do exame
            exam = Exame(
                nome_paciente=validated_data['nome_paciente'],
                data_nascimento=validated_data['data_nascimento'],
                idade=validated_data['idade'],
                sexo=validated_data['sexo'],
                data_exame=validated_data['data_exame'],
                tipo_atendimento=validated_data.get('tipo_atendimento'),
                medico_usuario=validated_data.get('medico_usuario'),
                medico_solicitante=validated_data.get('medico_solicitante'),
                indicacao=validated_data.get('indicacao')
            )
            
            return DatabaseManager.save_entity(exam)
            
        except (ValidationError, DatabaseError) as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao criar exame: {str(e)}")
    
    @staticmethod
    def update_exam(exam_id: int, exam_data: Dict[str, Any]) -> Exame:
        """Atualiza exame existente"""
        try:
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            # Validação de dados
            validated_data = DataValidator.validate_patient_data(exam_data)
            
            # Atualização dos campos
            exam.nome_paciente = validated_data['nome_paciente']
            exam.data_nascimento = validated_data['data_nascimento']
            exam.idade = validated_data['idade']
            exam.sexo = validated_data['sexo']
            exam.data_exame = validated_data['data_exame']
            exam.tipo_atendimento = validated_data.get('tipo_atendimento')
            exam.medico_usuario = validated_data.get('medico_usuario')
            exam.medico_solicitante = validated_data.get('medico_solicitante')
            exam.indicacao = validated_data.get('indicacao')
            exam.updated_at = datetime.utcnow()
            
            return DatabaseManager.update_entity(exam)
            
        except (ValidationError, DatabaseError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao atualizar exame: {str(e)}")
    
    @staticmethod
    def get_exam(exam_id: int) -> Optional[Exame]:
        """Obtém exame por ID"""
        return DatabaseManager.get_by_id(Exame, exam_id)
    
    @staticmethod
    def delete_exam(exam_id: int) -> bool:
        """Remove exame do sistema"""
        try:
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            # Verificar se pode ser deletado
            if ExamService._exam_has_dependencies(exam):
                raise BusinessRuleError("Exame possui dados associados e não pode ser removido")
            
            return DatabaseManager.delete_entity(exam)
            
        except (DatabaseError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao deletar exame: {str(e)}")
    
    @staticmethod
    def search_exams(search_term: str = None, limit: int = 50) -> List[Exame]:
        """Busca exames por critério"""
        try:
            if search_term:
                return DatabaseManager.search_by_field(Exame, 'nome_paciente', search_term)
            else:
                return DatabaseManager.get_all(Exame, 'created_at', limit)
        except DatabaseError as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao buscar exames: {str(e)}")
    
    @staticmethod
    def get_patient_exams(patient_name: str) -> List[Exame]:
        """Obtém todos os exames de um paciente"""
        return DatabaseManager.search_by_field(Exame, 'nome_paciente', patient_name)
    
    @staticmethod
    def get_recent_exams(limit: int = 10) -> List[Exame]:
        """Obtém exames mais recentes"""
        return DatabaseManager.get_all(Exame, 'created_at', limit)
    
    @staticmethod
    def get_exam_statistics() -> Dict[str, Any]:
        """Obtém estatísticas dos exames"""
        try:
            stats = DatabaseManager.get_statistics()
            
            # Estatísticas adicionais específicas de exames
            from sqlalchemy import func
            from app import db
            
            today = datetime.now().date()
            week_ago = datetime.now().date().replace(day=datetime.now().day - 7)
            
            exams_this_week = db.session.query(Exame).filter(
                func.date(Exame.created_at) >= week_ago
            ).count()
            
            stats.update({
                'exames_semana': exams_this_week,
                'media_idade': db.session.query(func.avg(Exame.idade)).scalar() or 0
            })
            
            return stats
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao obter estatísticas: {str(e)}")
    
    @staticmethod
    def _validate_business_rules(exam_data: Dict[str, Any]) -> None:
        """Valida regras de negócio específicas"""
        # Verificar se a data do exame não é futura
        exam_date = datetime.strptime(exam_data['data_exame'], '%d/%m/%Y').date()
        if exam_date > datetime.now().date():
            raise BusinessRuleError("Data do exame não pode ser futura")
        
        # Verificar idade mínima e máxima
        age = exam_data['idade']
        if age < 0 or age > 150:
            raise BusinessRuleError("Idade deve estar entre 0 e 150 anos")
    
    @staticmethod
    def _exam_has_dependencies(exam: Exame) -> bool:
        """Verifica se o exame possui dependências"""
        return bool(exam.parametros or exam.laudos)