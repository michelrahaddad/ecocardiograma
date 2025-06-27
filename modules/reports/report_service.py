"""
Serviço de Relatórios - Coordenação geral de relatórios

Serviço principal que coordena a geração de diferentes tipos
de relatórios e exportações do sistema.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from modules.core.database import DatabaseManager
from modules.core.exceptions import BusinessRuleError
from models import Exame

class ReportService:
    """Serviço coordenador de relatórios"""
    
    @staticmethod
    def generate_exam_summary(exam_id: int) -> Dict[str, Any]:
        """Gera resumo completo do exame"""
        try:
            from modules.exams.exam_service import ExamService
            from modules.exams.parameter_service import ParameterService
            from modules.reports.laudo_service import LaudoService
            
            exam = ExamService.get_exam(exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            parameters = ParameterService.get_parameters(exam_id)
            laudo = LaudoService.get_laudo(exam_id)
            
            summary = {
                'exam': {
                    'id': exam.id,
                    'patient_name': exam.nome_paciente,
                    'birth_date': exam.data_nascimento,
                    'age': exam.idade,
                    'gender': exam.sexo,
                    'exam_date': exam.data_exame,
                    'created_at': exam.created_at.isoformat() if exam.created_at else None
                },
                'has_parameters': parameters is not None,
                'has_laudo': laudo is not None,
                'completion_status': ReportService._calculate_completion_status(exam, parameters, laudo)
            }
            
            return summary
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao gerar resumo: {str(e)}")
    
    @staticmethod
    def generate_statistics_report(start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Gera relatório de estatísticas do sistema"""
        try:
            from sqlalchemy import func
            from app import db
            
            # Definir período se não fornecido
            if not end_date:
                end_date = datetime.now().date()
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Estatísticas básicas
            total_exams = db.session.query(Exame).count()
            period_exams = db.session.query(Exame).filter(
                func.date(Exame.created_at) >= start_date,
                func.date(Exame.created_at) <= end_date
            ).count()
            
            # Distribuição por gênero
            gender_stats = db.session.query(
                Exame.sexo,
                func.count(Exame.id)
            ).group_by(Exame.sexo).all()
            
            # Distribuição por faixa etária
            age_ranges = [
                (0, 17, 'Pediátrico'),
                (18, 65, 'Adulto'),
                (66, 150, 'Idoso')
            ]
            
            age_distribution = {}
            for min_age, max_age, label in age_ranges:
                count = db.session.query(Exame).filter(
                    Exame.idade >= min_age,
                    Exame.idade <= max_age
                ).count()
                age_distribution[label] = count
            
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'totals': {
                    'total_exams': total_exams,
                    'period_exams': period_exams
                },
                'gender_distribution': dict(gender_stats),
                'age_distribution': age_distribution,
                'generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao gerar relatório de estatísticas: {str(e)}")
    
    @staticmethod
    def generate_quality_report() -> Dict[str, Any]:
        """Gera relatório de qualidade dos dados"""
        try:
            from modules.exams.parameter_service import ParameterService
            from modules.reports.laudo_service import LaudoService
            
            total_exams = DatabaseManager.execute_query(
                lambda: Exame.query.count()
            )
            
            # Contar exames com parâmetros
            exams_with_params = DatabaseManager.execute_query(
                lambda: Exame.query.join(ParametrosEcocardiograma).count()
            )
            
            # Contar exames com laudos
            exams_with_laudos = DatabaseManager.execute_query(
                lambda: Exame.query.join(LaudoEcocardiograma).count()
            )
            
            # Calcular percentuais de completude
            param_completion = (exams_with_params / total_exams * 100) if total_exams > 0 else 0
            laudo_completion = (exams_with_laudos / total_exams * 100) if total_exams > 0 else 0
            
            quality_report = {
                'total_exams': total_exams,
                'data_completion': {
                    'parameters': {
                        'count': exams_with_params,
                        'percentage': round(param_completion, 2)
                    },
                    'laudos': {
                        'count': exams_with_laudos,
                        'percentage': round(laudo_completion, 2)
                    }
                },
                'quality_score': round((param_completion + laudo_completion) / 2, 2),
                'generated_at': datetime.now().isoformat()
            }
            
            return quality_report
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao gerar relatório de qualidade: {str(e)}")
    
    @staticmethod
    def _calculate_completion_status(exam, parameters, laudo) -> Dict[str, Any]:
        """Calcula status de completude do exame"""
        status = {
            'percentage': 0,
            'missing_items': [],
            'completed_items': []
        }
        
        total_items = 3  # Exame, Parâmetros, Laudo
        completed_items = 1  # Sempre tem o exame
        
        status['completed_items'].append('Dados do paciente')
        
        if parameters:
            completed_items += 1
            status['completed_items'].append('Parâmetros ecocardiográficos')
        else:
            status['missing_items'].append('Parâmetros ecocardiográficos')
        
        if laudo:
            completed_items += 1
            status['completed_items'].append('Laudo médico')
        else:
            status['missing_items'].append('Laudo médico')
        
        status['percentage'] = round((completed_items / total_items) * 100, 1)
        
        return status