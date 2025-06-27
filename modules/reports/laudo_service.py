"""
Serviço de Laudos - Lógica para laudos médicos

Centraliza toda a lógica relacionada aos laudos médicos,
incluindo criação, edição e templates pré-definidos.
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
from models import LaudoEcocardiograma, Exame
from modules.core.database import DatabaseManager
from modules.core.validators import DataValidator
from modules.core.exceptions import ValidationError, DatabaseError, BusinessRuleError

class LaudoService:
    """Serviço centralizado para laudos ecocardiográficos"""
    
    # Templates de laudos pré-definidos
    LAUDO_TEMPLATES = {
        'normal_adulto': {
            'modo_m_bidimensional': 'Exame dentro dos limites da normalidade para a idade. Cavidades cardíacas com dimensões preservadas. Função sistólica do ventrículo esquerdo normal.',
            'doppler_convencional': 'Fluxos intracardíacos normais. Ausência de regurgitações valvares significativas.',
            'doppler_tecidual': 'Velocidades do anel mitral dentro da normalidade, sugerindo função diastólica preservada.',
            'conclusao': 'Ecocardiograma transtorácico normal.',
            'recomendacoes': 'Manter acompanhamento clínico de rotina.'
        },
        'disfuncao_sistolica': {
            'modo_m_bidimensional': 'Disfunção sistólica do ventrículo esquerdo com fração de ejeção reduzida.',
            'doppler_convencional': 'Avaliar regurgitações valvares secundárias.',
            'doppler_tecidual': 'Velocidades do anel mitral alteradas.',
            'conclusao': 'Disfunção sistólica do ventrículo esquerdo.',
            'recomendacoes': 'Acompanhamento cardiológico especializado. Considerar otimização de terapia medicamentosa.'
        },
        'pediatrico_normal': {
            'modo_m_bidimensional': 'Exame dentro dos limites da normalidade para a idade pediátrica. Cavidades cardíacas proporcionais ao peso e altura.',
            'doppler_convencional': 'Fluxos intracardíacos normais para a idade. Ausência de shunts.',
            'doppler_tecidual': 'Função diastólica preservada para a faixa etária.',
            'conclusao': 'Ecocardiograma pediátrico normal.',
            'recomendacoes': 'Acompanhamento pediátrico de rotina.'
        }
    }
    
    @staticmethod
    def save_laudo(exam_id: int, laudo_data: Dict[str, Any]) -> LaudoEcocardiograma:
        """Salva laudo médico com validação"""
        try:
            # Verificar se exame existe
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            # Validar dados
            validated_data = LaudoService._validate_laudo_data(laudo_data)
            
            # Verificar se já existe laudo para este exame
            existing_laudo = DatabaseManager.execute_query(
                lambda: LaudoEcocardiograma.query.filter_by(exame_id=exam_id).first()
            )
            
            if existing_laudo:
                # Atualizar existente
                return LaudoService._update_existing_laudo(existing_laudo, validated_data)
            else:
                # Criar novo
                return LaudoService._create_new_laudo(exam_id, validated_data)
                
        except (ValidationError, DatabaseError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao salvar laudo: {str(e)}")
    
    @staticmethod
    def get_laudo(exam_id: int) -> Optional[LaudoEcocardiograma]:
        """Obtém laudo de um exame"""
        try:
            return DatabaseManager.execute_query(
                lambda: LaudoEcocardiograma.query.filter_by(exame_id=exam_id).first()
            )
        except DatabaseError as e:
            raise e
    
    @staticmethod
    def get_laudo_templates() -> Dict[str, Dict[str, str]]:
        """Obtém templates de laudos disponíveis"""
        return LaudoService.LAUDO_TEMPLATES.copy()
    
    @staticmethod
    def apply_template(template_name: str, patient_age: int = None) -> Dict[str, str]:
        """Aplica template de laudo baseado no tipo e idade"""
        try:
            if template_name not in LaudoService.LAUDO_TEMPLATES:
                raise BusinessRuleError(f"Template '{template_name}' não encontrado")
            
            template = LaudoService.LAUDO_TEMPLATES[template_name].copy()
            
            # Personalizar template baseado na idade se fornecida
            if patient_age is not None:
                template = LaudoService._customize_template_by_age(template, patient_age)
            
            return template
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao aplicar template: {str(e)}")
    
    @staticmethod
    def generate_auto_laudo(exam_id: int) -> Dict[str, str]:
        """Gera laudo automático baseado nos parâmetros do exame"""
        try:
            from modules.exams.parameter_service import ParameterService
            
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            parameters = ParameterService.get_parameters(exam_id)
            if not parameters:
                raise BusinessRuleError("Parâmetros do exame não encontrados")
            
            # Determinar template baseado nos achados
            template_name = LaudoService._determine_template_from_parameters(parameters, exam.idade)
            
            # Aplicar template
            auto_laudo = LaudoService.apply_template(template_name, exam.idade)
            
            # Personalizar baseado nos parâmetros específicos
            auto_laudo = LaudoService._customize_laudo_from_parameters(auto_laudo, parameters)
            
            return auto_laudo
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao gerar laudo automático: {str(e)}")
    
    @staticmethod
    def _validate_laudo_data(laudo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do laudo"""
        validated = {}
        
        for field, value in laudo_data.items():
            if value is not None:
                # Sanitizar texto
                validated[field] = DataValidator.sanitize_string(str(value), 5000)
        
        return validated
    
    @staticmethod
    def _create_new_laudo(exam_id: int, validated_data: Dict[str, Any]) -> LaudoEcocardiograma:
        """Cria novo laudo"""
        laudo = LaudoEcocardiograma(exame_id=exam_id)
        
        # Definir campos
        for field, value in validated_data.items():
            if hasattr(laudo, field):
                setattr(laudo, field, value)
        
        return DatabaseManager.save_entity(laudo)
    
    @staticmethod
    def _update_existing_laudo(existing_laudo: LaudoEcocardiograma, validated_data: Dict[str, Any]) -> LaudoEcocardiograma:
        """Atualiza laudo existente"""
        # Atualizar campos
        for field, value in validated_data.items():
            if hasattr(existing_laudo, field):
                setattr(existing_laudo, field, value)
        
        existing_laudo.updated_at = datetime.utcnow()
        
        return DatabaseManager.update_entity(existing_laudo)
    
    @staticmethod
    def _customize_template_by_age(template: Dict[str, str], age: int) -> Dict[str, str]:
        """Personaliza template baseado na idade"""
        if age < 18:
            # Ajustes para pacientes pediátricos
            for key, value in template.items():
                template[key] = value.replace('para a idade', 'para a idade pediátrica')
        elif age > 65:
            # Ajustes para pacientes idosos
            for key, value in template.items():
                template[key] = value.replace('normal', 'adequado para a idade')
        
        return template
    
    @staticmethod
    def _determine_template_from_parameters(parameters, age: int) -> str:
        """Determina template baseado nos parâmetros"""
        # Lógica simplificada - pode ser expandida
        if age < 18:
            return 'pediatrico_normal'
        
        # Verificar função sistólica
        if hasattr(parameters, 'fracao_ejecao') and parameters.fracao_ejecao:
            if parameters.fracao_ejecao < 50:
                return 'disfuncao_sistolica'
        
        return 'normal_adulto'
    
    @staticmethod
    def _customize_laudo_from_parameters(laudo: Dict[str, str], parameters) -> Dict[str, str]:
        """Personaliza laudo baseado nos parâmetros específicos"""
        customized = laudo.copy()
        
        # Adicionar informações específicas baseadas nos parâmetros
        if hasattr(parameters, 'fracao_ejecao') and parameters.fracao_ejecao:
            fe_text = f" Fração de ejeção: {parameters.fracao_ejecao}%."
            customized['modo_m_bidimensional'] += fe_text
        
        if hasattr(parameters, 'pressao_sistolica_vd') and parameters.pressao_sistolica_vd:
            if parameters.pressao_sistolica_vd > 35:
                psap_text = f" Pressão sistólica estimada do VD: {parameters.pressao_sistolica_vd} mmHg (elevada)."
                customized['doppler_convencional'] += psap_text
        
        return customized