"""
Serviço de Parâmetros - Lógica para parâmetros de ecocardiograma

Centraliza toda a lógica relacionada aos parâmetros ecocardiográficos,
incluindo validação, cálculos automáticos e persistência.
"""

from typing import Dict, Optional, Any
from datetime import datetime
from models import ParametrosEcocardiograma, Exame
from modules.core.database import DatabaseManager
from modules.core.validators import DataValidator
from modules.core.exceptions import ValidationError, DatabaseError, BusinessRuleError

class ParameterService:
    """Serviço centralizado para parâmetros ecocardiográficos"""
    
    # Ranges de valores normais para validação
    NORMAL_RANGES = {
        'peso': (0.5, 300),
        'altura': (0.3, 2.5),
        'frequencia_cardiaca': (30, 220),
        'atrio_esquerdo': (1.0, 8.0),
        'raiz_aorta': (1.0, 6.0),
        'diametro_diastolico_final_ve': (2.0, 8.0),
        'fracao_ejecao': (10, 90)
    }
    
    @staticmethod
    def save_parameters(exam_id: int, param_data: Dict[str, Any]) -> ParametrosEcocardiograma:
        """Salva parâmetros do ecocardiograma com validação"""
        try:
            # Verificar se exame existe
            exam = DatabaseManager.get_by_id(Exame, exam_id)
            if not exam:
                raise BusinessRuleError("Exame não encontrado")
            
            # Validar dados
            validated_data = ParameterService._validate_parameters(param_data)
            
            # Verificar se já existe parâmetros para este exame
            existing_params = DatabaseManager.execute_query(
                lambda: ParametrosEcocardiograma.query.filter_by(exame_id=exam_id).first()
            )
            
            if existing_params:
                # Atualizar existente
                return ParameterService._update_existing_parameters(existing_params, validated_data)
            else:
                # Criar novo
                return ParameterService._create_new_parameters(exam_id, validated_data)
                
        except (ValidationError, DatabaseError, BusinessRuleError) as e:
            raise e
        except Exception as e:
            raise BusinessRuleError(f"Erro ao salvar parâmetros: {str(e)}")
    
    @staticmethod
    def get_parameters(exam_id: int) -> Optional[ParametrosEcocardiograma]:
        """Obtém parâmetros de um exame"""
        try:
            return DatabaseManager.execute_query(
                lambda: ParametrosEcocardiograma.query.filter_by(exame_id=exam_id).first()
            )
        except DatabaseError as e:
            raise e
    
    @staticmethod
    def calculate_derived_values(params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula valores derivados automaticamente"""
        try:
            calculated = params.copy()
            
            # Cálculo da Superfície Corporal (Fórmula de Mosteller)
            if params.get('peso') and params.get('altura'):
                peso = float(params['peso'])
                altura = float(params['altura']) * 100  # converter para cm
                sc = ((peso * altura) / 3600) ** 0.5
                calculated['superficie_corporal'] = round(sc, 2)
            
            # Relação AE/Ao
            if params.get('atrio_esquerdo') and params.get('raiz_aorta'):
                ae = float(params['atrio_esquerdo'])
                ao = float(params['raiz_aorta'])
                if ao > 0:
                    calculated['relacao_atrio_esquerdo_aorta'] = round(ae / ao, 2)
            
            # Percentual de Encurtamento
            if params.get('diametro_diastolico_final_ve') and params.get('diametro_sistolico_final'):
                dd = float(params['diametro_diastolico_final_ve'])
                ds = float(params['diametro_sistolico_final'])
                if dd > 0:
                    pe = ((dd - ds) / dd) * 100
                    calculated['percentual_encurtamento'] = round(pe, 1)
            
            # Relação Septo/Parede Posterior
            if params.get('espessura_diastolica_septo') and params.get('espessura_diastolica_ppve'):
                septo = float(params['espessura_diastolica_septo'])
                pp = float(params['espessura_diastolica_ppve'])
                if pp > 0:
                    calculated['relacao_septo_parede_posterior'] = round(septo / pp, 2)
            
            # Volume de Ejeção
            if params.get('volume_diastolico_final') and params.get('volume_sistolico_final'):
                vdf = float(params['volume_diastolico_final'])
                vsf = float(params['volume_sistolico_final'])
                calculated['volume_ejecao'] = round(vdf - vsf, 1)
            
            # Relação E/A
            if params.get('onda_e') and params.get('onda_a'):
                e = float(params['onda_e'])
                a = float(params['onda_a'])
                if a > 0:
                    calculated['relacao_e_a'] = round(e / a, 2)
            
            # Relação E/E'
            if params.get('onda_e') and params.get('onda_e_linha'):
                e = float(params['onda_e'])
                e_linha = float(params['onda_e_linha'])
                if e_linha > 0:
                    calculated['relacao_e_e_linha'] = round(e / e_linha, 1)
            
            # Pressão Sistólica VD
            if params.get('gradiente_tricuspide'):
                grad = float(params['gradiente_tricuspide'])
                # Pressão sistólica VD = 4 x (velocidade)² + PVC (assumindo PVC = 10)
                calculated['pressao_sistolica_vd'] = round((4 * grad * grad) + 10, 0)
            
            return calculated
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao calcular valores derivados: {str(e)}")
    
    @staticmethod
    def _validate_parameters(param_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida parâmetros ecocardiográficos"""
        validated = {}
        
        for field, value in param_data.items():
            if value is not None and str(value).strip() != '':
                try:
                    # Converter para float se numérico
                    if field in ParameterService.NORMAL_RANGES:
                        num_value = DataValidator.validate_numeric_range(
                            value, 
                            ParameterService.NORMAL_RANGES[field][0],
                            ParameterService.NORMAL_RANGES[field][1],
                            field
                        )
                        validated[field] = num_value
                    else:
                        # Para campos de texto
                        if isinstance(value, str):
                            validated[field] = DataValidator.sanitize_string(value, 50)
                        else:
                            validated[field] = float(value) if value is not None else None
                except (ValueError, ValidationError):
                    # Ignorar valores inválidos em vez de falhar
                    continue
        
        return validated
    
    @staticmethod
    def _create_new_parameters(exam_id: int, validated_data: Dict[str, Any]) -> ParametrosEcocardiograma:
        """Cria novos parâmetros"""
        # Calcular valores derivados
        calculated_data = ParameterService.calculate_derived_values(validated_data)
        
        params = ParametrosEcocardiograma(exame_id=exam_id)
        
        # Definir todos os campos
        for field, value in calculated_data.items():
            if hasattr(params, field):
                setattr(params, field, value)
        
        return DatabaseManager.save_entity(params)
    
    @staticmethod
    def _update_existing_parameters(existing_params: ParametrosEcocardiograma, validated_data: Dict[str, Any]) -> ParametrosEcocardiograma:
        """Atualiza parâmetros existentes"""
        # Calcular valores derivados
        calculated_data = ParameterService.calculate_derived_values(validated_data)
        
        # Atualizar campos
        for field, value in calculated_data.items():
            if hasattr(existing_params, field):
                setattr(existing_params, field, value)
        
        existing_params.updated_at = datetime.utcnow()
        
        return DatabaseManager.update_entity(existing_params)