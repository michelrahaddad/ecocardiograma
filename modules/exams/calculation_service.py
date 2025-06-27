"""
Serviço de Cálculos - Cálculos ecocardiográficos especializados

Módulo dedicado aos cálculos complexos e fórmulas específicas
da cardiologia para ecocardiogramas.
"""

import math
from typing import Dict, Optional, Any, Tuple
from modules.core.exceptions import BusinessRuleError

class CalculationService:
    """Serviço especializado em cálculos ecocardiográficos"""
    
    # Constantes para cálculos
    GRAVITY = 9.8  # m/s²
    
    @staticmethod
    def calculate_body_surface_area(weight: float, height: float, formula: str = "mosteller") -> float:
        """Calcula superfície corporal usando diferentes fórmulas"""
        try:
            if formula.lower() == "mosteller":
                # Fórmula de Mosteller: √(peso × altura_cm / 3600)
                height_cm = height * 100
                return math.sqrt((weight * height_cm) / 3600)
            
            elif formula.lower() == "dubois":
                # Fórmula de DuBois: 0.007184 × peso^0.425 × altura_cm^0.725
                height_cm = height * 100
                return 0.007184 * (weight ** 0.425) * (height_cm ** 0.725)
            
            else:
                raise BusinessRuleError(f"Fórmula '{formula}' não reconhecida")
                
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo da superfície corporal: {str(e)}")
    
    @staticmethod
    def calculate_ejection_fraction(edv: float, esv: float) -> float:
        """Calcula fração de ejeção: (VDF - VSF) / VDF × 100"""
        try:
            if edv <= 0:
                raise BusinessRuleError("Volume diastólico final deve ser maior que zero")
            
            ef = ((edv - esv) / edv) * 100
            return round(ef, 1)
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo da fração de ejeção: {str(e)}")
    
    @staticmethod
    def calculate_lv_mass(ivs: float, lvid: float, pw: float, bsa: float = None) -> Tuple[float, Optional[float]]:
        """Calcula massa do ventrículo esquerdo e índice de massa"""
        try:
            # Fórmula ASE: 0.8 × {1.04 × [(SIV + DDVE + PP)³ - DDVE³]} + 0.6
            mass = 0.8 * (1.04 * ((ivs + lvid + pw) ** 3 - lvid ** 3)) + 0.6
            
            mass_index = None
            if bsa and bsa > 0:
                mass_index = mass / bsa
            
            return round(mass, 1), round(mass_index, 1) if mass_index else None
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo da massa do VE: {str(e)}")
    
    @staticmethod
    def calculate_cardiac_output(stroke_volume: float, heart_rate: int) -> float:
        """Calcula débito cardíaco: VS × FC / 1000"""
        try:
            if heart_rate <= 0:
                raise BusinessRuleError("Frequência cardíaca deve ser maior que zero")
            
            co = (stroke_volume * heart_rate) / 1000
            return round(co, 2)
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo do débito cardíaco: {str(e)}")
    
    @staticmethod
    def calculate_rvsp(tr_velocity: float, ra_pressure: float = 10) -> float:
        """Calcula pressão sistólica do VD: 4 × V² + PVC"""
        try:
            if tr_velocity <= 0:
                raise BusinessRuleError("Velocidade da tricúspide deve ser maior que zero")
            
            rvsp = (4 * tr_velocity * tr_velocity) + ra_pressure
            return round(rvsp, 0)
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo da PSAP: {str(e)}")
    
    @staticmethod
    def calculate_mitral_valve_area(peak_velocity: float, vti: float) -> float:
        """Calcula área da válvula mitral pelo tempo de meia pressão"""
        try:
            if peak_velocity <= 0 or vti <= 0:
                raise BusinessRuleError("Velocidades devem ser maiores que zero")
            
            # Fórmula simplificada: 220 / tempo de meia pressão
            # THT aproximado = VTI / velocidade de pico
            tht = vti / peak_velocity
            area = 220 / (tht * 1000)  # convertendo para ms
            
            return round(area, 2)
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo da área mitral: {str(e)}")
    
    @staticmethod
    def calculate_diastolic_function_grade(e_velocity: float, a_velocity: float, 
                                         e_prime: float, la_volume: float = None) -> Dict[str, Any]:
        """Avalia função diastólica baseado nas diretrizes"""
        try:
            result = {
                'e_a_ratio': None,
                'e_e_prime_ratio': None,
                'grade': 'Indeterminado',
                'description': ''
            }
            
            if e_velocity > 0 and a_velocity > 0:
                result['e_a_ratio'] = round(e_velocity / a_velocity, 2)
            
            if e_velocity > 0 and e_prime > 0:
                result['e_e_prime_ratio'] = round(e_velocity / e_prime, 1)
            
            # Gradação simplificada
            e_a = result['e_a_ratio']
            e_e_prime = result['e_e_prime_ratio']
            
            if e_a and e_e_prime:
                if e_a < 0.8 and e_e_prime < 8:
                    result['grade'] = 'Normal'
                    result['description'] = 'Função diastólica normal'
                elif e_a < 0.8 and e_e_prime >= 8:
                    result['grade'] = 'Grau I'
                    result['description'] = 'Relaxamento alterado'
                elif 0.8 <= e_a <= 2.0:
                    result['grade'] = 'Grau II'
                    result['description'] = 'Pseudonormalização'
                elif e_a > 2.0 and e_e_prime > 14:
                    result['grade'] = 'Grau III'
                    result['description'] = 'Padrão restritivo'
            
            return result
            
        except Exception as e:
            raise BusinessRuleError(f"Erro na avaliação da função diastólica: {str(e)}")
    
    @staticmethod
    def calculate_pediatric_zscore(value: float, age_months: int, parameter: str) -> Optional[float]:
        """Calcula Z-score para parâmetros pediátricos"""
        try:
            # Tabelas de referência simplificadas (necessário implementar tabelas completas)
            reference_tables = {
                'aortic_root': {
                    'mean': lambda age: 1.5 + (age * 0.02),  # Exemplo simplificado
                    'sd': 0.3
                },
                'left_atrium': {
                    'mean': lambda age: 2.0 + (age * 0.03),
                    'sd': 0.4
                }
            }
            
            if parameter not in reference_tables:
                return None
            
            ref = reference_tables[parameter]
            expected_mean = ref['mean'](age_months)
            sd = ref['sd']
            
            zscore = (value - expected_mean) / sd
            return round(zscore, 2)
            
        except Exception as e:
            raise BusinessRuleError(f"Erro no cálculo do Z-score: {str(e)}")
    
    @staticmethod
    def validate_hemodynamics(parameters: Dict[str, float]) -> Dict[str, str]:
        """Valida parâmetros hemodinâmicos e retorna alertas"""
        alerts = {}
        
        try:
            # Verificar fração de ejeção
            if 'fracao_ejecao' in parameters:
                fe = parameters['fracao_ejecao']
                if fe < 40:
                    alerts['fracao_ejecao'] = 'Fração de ejeção reduzida (<40%)'
                elif fe < 50:
                    alerts['fracao_ejecao'] = 'Fração de ejeção levemente reduzida (40-49%)'
            
            # Verificar pressão sistólica do VD
            if 'pressao_sistolica_vd' in parameters:
                psap = parameters['pressao_sistolica_vd']
                if psap > 35:
                    alerts['pressao_sistolica_vd'] = f'Hipertensão pulmonar suspeita (PSAP: {psap} mmHg)'
            
            # Verificar relação E/E'
            if 'relacao_e_e_linha' in parameters:
                e_e_prime = parameters['relacao_e_e_linha']
                if e_e_prime > 14:
                    alerts['relacao_e_e_linha'] = 'Pressão de enchimento elevada (E/E\' > 14)'
            
            return alerts
            
        except Exception as e:
            raise BusinessRuleError(f"Erro na validação hemodinâmica: {str(e)}")