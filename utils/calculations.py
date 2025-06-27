"""
Sistema de Ecocardiograma - Grupo Vidah
Funções de Cálculo para Parâmetros Ecocardiográficos
"""

import math
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calcular_parametros_derivados(parametros):
    """
    Calcula todos os parâmetros derivados baseados nos valores inseridos
    
    Args:
        parametros: Objeto ParametrosEcocardiograma com os valores básicos
    """
    try:
        # Cálculos antropométricos
        calcular_superficie_corporal(parametros)
        
        # Cálculos ecocardiográficos básicos
        calcular_relacao_atrio_aorta(parametros)
        calcular_percentual_encurtamento(parametros)
        calcular_relacao_septo_parede_posterior(parametros)
        
        # Cálculos de volumes usando Teichholz
        calcular_volumes_teichholz(parametros)
        calcular_volumes_funcao_sistolica(parametros)
        
        # Massa VE usando fórmula ASE corrigida
        calcular_massa_ve_ase_corrigida(parametros)
        
        # Gradientes usando Bernoulli
        calcular_gradientes_bernoulli(parametros)
        
        # Cálculos de função diastólica
        calcular_funcao_diastolica(parametros)
        
        # Cálculos de pressões
        calcular_pressoes_ventriculares(parametros)
        
        logger.info("Cálculos de parâmetros derivados concluídos com sucesso")
        
    except Exception as e:
        logger.error(f"Erro nos cálculos de parâmetros: {str(e)}")
        raise

def calcular_superficie_corporal(parametros):
    """
    Calcula a superfície corporal usando a fórmula de DuBois
    BSA = 0.007184 × altura^0.725 × peso^0.425
    """
    if parametros.peso and parametros.altura and parametros.peso > 0 and parametros.altura > 0:
        try:
            bsa = 0.007184 * (parametros.altura ** 0.725) * (parametros.peso ** 0.425)
            parametros.superficie_corporal = round(bsa, 2)
            logger.debug(f"Superfície corporal calculada: {parametros.superficie_corporal} m²")
        except Exception as e:
            logger.warning(f"Erro no cálculo da superfície corporal: {e}")

def calcular_relacao_atrio_aorta(parametros):
    """
    Calcula a relação entre átrio esquerdo e aorta
    """
    if parametros.atrio_esquerdo and parametros.raiz_aorta and parametros.raiz_aorta > 0:
        try:
            relacao = parametros.atrio_esquerdo / parametros.raiz_aorta
            parametros.relacao_atrio_esquerdo_aorta = round(relacao, 2)
            logger.debug(f"Relação AE/Ao calculada: {parametros.relacao_atrio_esquerdo_aorta}")
        except Exception as e:
            logger.warning(f"Erro no cálculo da relação AE/Ao: {e}")

def calcular_percentual_encurtamento(parametros):
    """
    Calcula o percentual de encurtamento do ventrículo esquerdo
    % Encurtamento = ((DDVE - DSVE) / DDVE) × 100
    """
    if (parametros.diametro_diastolico_final_ve and 
        parametros.diametro_sistolico_final and 
        parametros.diametro_diastolico_final_ve > 0):
        try:
            encurtamento = ((parametros.diametro_diastolico_final_ve - parametros.diametro_sistolico_final) / 
                           parametros.diametro_diastolico_final_ve) * 100
            parametros.percentual_encurtamento = round(encurtamento, 1)
            logger.debug(f"Percentual de encurtamento calculado: {parametros.percentual_encurtamento}%")
        except Exception as e:
            logger.warning(f"Erro no cálculo do percentual de encurtamento: {e}")

def calcular_relacao_septo_parede_posterior(parametros):
    """
    Calcula a relação entre espessura do septo e parede posterior
    """
    if (parametros.espessura_diastolica_septo and 
        parametros.espessura_diastolica_ppve and 
        parametros.espessura_diastolica_ppve > 0):
        try:
            relacao = parametros.espessura_diastolica_septo / parametros.espessura_diastolica_ppve
            parametros.relacao_septo_parede_posterior = round(relacao, 2)
            logger.debug(f"Relação septo/PP calculada: {parametros.relacao_septo_parede_posterior}")
        except Exception as e:
            logger.warning(f"Erro no cálculo da relação septo/PP: {e}")

def calcular_volumes_funcao_sistolica(parametros):
    """
    Calcula volumes de ejeção e fração de ejeção
    """
    # Volume de ejeção
    if parametros.volume_diastolico_final and parametros.volume_sistolico_final:
        try:
            volume_ejecao = parametros.volume_diastolico_final - parametros.volume_sistolico_final
            parametros.volume_ejecao = round(volume_ejecao, 1)
            logger.debug(f"Volume de ejeção calculado: {parametros.volume_ejecao} mL")
        except Exception as e:
            logger.warning(f"Erro no cálculo do volume de ejeção: {e}")
    
    # Fração de ejeção
    if (parametros.volume_diastolico_final and 
        parametros.volume_sistolico_final and 
        parametros.volume_diastolico_final > 0):
        try:
            fracao_ejecao = ((parametros.volume_diastolico_final - parametros.volume_sistolico_final) / 
                            parametros.volume_diastolico_final) * 100
            parametros.fracao_ejecao = round(fracao_ejecao, 1)
            logger.debug(f"Fração de ejeção calculada: {parametros.fracao_ejecao}%")
        except Exception as e:
            logger.warning(f"Erro no cálculo da fração de ejeção: {e}")

def calcular_volumes_teichholz(parametros):
    """
    Calcula volumes ventriculares usando método de Teichholz
    """
    # Volume Diastólico Final - método de Teichholz
    if parametros.diametro_diastolico_final_ve and parametros.diametro_diastolico_final_ve > 0:
        try:
            # Converter de mm para cm
            ddve_cm = parametros.diametro_diastolico_final_ve / 10
            # VDF = (7 × (DDVE)³) / (2.4 + DDVE)
            vdf = (7 * (ddve_cm ** 3)) / (2.4 + ddve_cm)
            parametros.volume_diastolico_final = round(vdf, 1)
            logger.debug(f"VDF (Teichholz) calculado: {parametros.volume_diastolico_final} mL")
        except Exception as e:
            logger.warning(f"Erro no cálculo do VDF: {e}")
    
    # Volume Sistólico Final - método de Teichholz
    if parametros.diametro_sistolico_final and parametros.diametro_sistolico_final > 0:
        try:
            # Converter de mm para cm
            dsve_cm = parametros.diametro_sistolico_final / 10
            # VSF = (7 × (DSVE)³) / (2.4 + DSVE)
            vsf = (7 * (dsve_cm ** 3)) / (2.4 + dsve_cm)
            parametros.volume_sistolico_final = round(vsf, 1)
            logger.debug(f"VSF (Teichholz) calculado: {parametros.volume_sistolico_final} mL")
        except Exception as e:
            logger.warning(f"Erro no cálculo do VSF: {e}")

def calcular_massa_ve_ase_corrigida(parametros):
    """
    Calcula a massa do VE usando fórmula ASE corrigida
    IMPORTANTE: Fórmula exige valores em centímetros (cm)
    """
    if (parametros.diametro_diastolico_final_ve and 
        parametros.espessura_diastolica_septo and 
        parametros.espessura_diastolica_ppve):
        try:
            # CRÍTICO: Converter de mm para cm para a fórmula ASE
            ddve_cm = parametros.diametro_diastolico_final_ve / 10  # mm → cm
            septo_cm = parametros.espessura_diastolica_septo / 10   # mm → cm
            pp_cm = parametros.espessura_diastolica_ppve / 10       # mm → cm
            
            # Fórmula ASE corrigida: Massa VE = 0.8 × [1.04 × ((DDVE + Septo + PP)³ - (DDVE)³)] + 0.6
            # Todos os valores devem estar em cm conforme especificação médica
            soma_paredes = ddve_cm + septo_cm + pp_cm
            massa_ve = 0.8 * (1.04 * (soma_paredes**3 - ddve_cm**3)) + 0.6
            parametros.massa_ve = round(massa_ve, 1)
            logger.debug(f"Massa VE (ASE corrigida) calculada: {parametros.massa_ve} g (DDVE:{ddve_cm}cm, Septo:{septo_cm}cm, PP:{pp_cm}cm)")
            
            # Índice de massa VE
            if parametros.superficie_corporal and parametros.superficie_corporal > 0:
                indice_massa = massa_ve / parametros.superficie_corporal
                parametros.indice_massa_ve = round(indice_massa, 1)
                logger.debug(f"Índice massa VE calculado: {parametros.indice_massa_ve} g/m²")
                
        except Exception as e:
            logger.warning(f"Erro no cálculo da massa VE: {e}")

def calcular_gradientes_bernoulli(parametros):
    """
    Calcula gradientes usando equação de Bernoulli modificada
    """
    # Gradiente VD→AP
    if parametros.fluxo_pulmonar and parametros.fluxo_pulmonar > 0:
        try:
            gradiente = 4 * (parametros.fluxo_pulmonar ** 2)
            parametros.gradiente_vd_ap = round(gradiente, 1)
            logger.debug(f"Gradiente VD→AP calculado: {parametros.gradiente_vd_ap} mmHg")
        except Exception as e:
            logger.warning(f"Erro no cálculo do gradiente VD→AP: {e}")
    
    # Gradiente VE→AO
    if parametros.fluxo_aortico and parametros.fluxo_aortico > 0:
        try:
            gradiente = 4 * (parametros.fluxo_aortico ** 2)
            parametros.gradiente_ve_ao = round(gradiente, 1)
            logger.debug(f"Gradiente VE→AO calculado: {parametros.gradiente_ve_ao} mmHg")
        except Exception as e:
            logger.warning(f"Erro no cálculo do gradiente VE→AO: {e}")
    
    # Gradiente AE→VE
    if parametros.fluxo_mitral and parametros.fluxo_mitral > 0:
        try:
            gradiente = 4 * (parametros.fluxo_mitral ** 2)
            parametros.gradiente_ae_ve = round(gradiente, 1)
            logger.debug(f"Gradiente AE→VE calculado: {parametros.gradiente_ae_ve} mmHg")
        except Exception as e:
            logger.warning(f"Erro no cálculo do gradiente AE→VE: {e}")
    
    # Gradiente AD→VD (Tricúspide)
    if parametros.fluxo_tricuspide and parametros.fluxo_tricuspide > 0:
        try:
            gradiente = 4 * (parametros.fluxo_tricuspide ** 2)
            parametros.gradiente_ad_vd = round(gradiente, 1)
            parametros.gradiente_tricuspide = round(gradiente, 1)  # Mesmo valor
            logger.debug(f"Gradiente AD→VD/IT calculado: {parametros.gradiente_ad_vd} mmHg")
        except Exception as e:
            logger.warning(f"Erro no cálculo do gradiente AD→VD: {e}")

def calcular_funcao_diastolica(parametros):
    """
    Calcula parâmetros de função diastólica
    """
    # Função diastólica removida conforme padronização médica
    pass

def calcular_pressoes_ventriculares(parametros):
    """
    Calcula pressões ventriculares direitas
    """
    # PSAP (Pressão Sistólica da Artéria Pulmonar)
    if parametros.gradiente_tricuspide:
        try:
            # PSAP = Gradiente IT + Pressão atrial direita (assumir 10 mmHg)
            psap = parametros.gradiente_tricuspide + 10
            parametros.pressao_sistolica_vd = round(psap, 1)
            logger.debug(f"PSAP calculada: {parametros.pressao_sistolica_vd} mmHg")
        except Exception as e:
            logger.warning(f"Erro no cálculo da PSAP: {e}")

def validar_parametros_normais(parametros, idade=None, sexo=None):
    """
    Valida se os parâmetros estão dentro dos valores de referência
    
    Returns:
        dict: Dicionário com os resultados da validação
    """
    resultados = {}
    
    try:
        # Valores de referência (podem variar com idade e sexo)
        referencias = obter_valores_referencia(idade, sexo)
        
        # Validar cada parâmetro
        if parametros.frequencia_cardiaca:
            resultados['frequencia_cardiaca'] = validar_faixa(
                parametros.frequencia_cardiaca, 
                referencias['frequencia_cardiaca']['min'], 
                referencias['frequencia_cardiaca']['max']
            )
        
        if parametros.atrio_esquerdo:
            resultados['atrio_esquerdo'] = validar_faixa(
                parametros.atrio_esquerdo,
                referencias['atrio_esquerdo']['min'],
                referencias['atrio_esquerdo']['max']
            )
        
        if parametros.fracao_ejecao:
            resultados['fracao_ejecao'] = {
                'normal': parametros.fracao_ejecao >= referencias['fracao_ejecao']['min'],
                'valor': parametros.fracao_ejecao,
                'referencia': f"≥{referencias['fracao_ejecao']['min']}%"
            }
        
        # Adicionar mais validações conforme necessário
        
    except Exception as e:
        logger.error(f"Erro na validação de parâmetros: {e}")
        
    return resultados

def validar_faixa(valor, minimo, maximo):
    """
    Valida se um valor está dentro de uma faixa normal
    """
    return {
        'normal': minimo <= valor <= maximo,
        'valor': valor,
        'referencia': f"{minimo}-{maximo}"
    }

def obter_valores_referencia(idade=None, sexo=None):
    """
    Obtém valores de referência baseados em idade e sexo
    """
    # Valores de referência padrão para adultos
    referencias = {
        'frequencia_cardiaca': {'min': 60, 'max': 100},
        'atrio_esquerdo': {'min': 2.7, 'max': 3.8},
        'raiz_aorta': {'min': 2.1, 'max': 3.4},
        'diametro_diastolico_final_ve': {'min': 3.5, 'max': 5.6},
        'diametro_sistolico_final': {'min': 2.1, 'max': 4.0},
        'percentual_encurtamento': {'min': 25, 'max': 45},
        'fracao_ejecao': {'min': 55},
        'espessura_diastolica_septo': {'min': 0.6, 'max': 1.1},
        'espessura_diastolica_ppve': {'min': 0.6, 'max': 1.1},
        'relacao_e_a': {'min': 0.8, 'max': 1.5},
        'pressao_sistolica_vd': {'max': 35}
    }
    
    # Ajustes baseados em sexo
    if sexo == 'Masculino':
        referencias['indice_massa_ve'] = {'max': 115}
    elif sexo == 'Feminino':
        referencias['indice_massa_ve'] = {'max': 95}
    
    # Ajustes baseados em idade (implementar conforme necessário)
    if idade:
        if idade > 65:
            # Ajustes para idosos
            referencias['relacao_e_a']['min'] = 0.7
        elif idade < 18:
            # Ajustes para crianças/adolescentes
            pass
    
    return referencias

def calcular_z_score(valor, media_populacional, desvio_padrao):
    """
    Calcula o Z-score para um parâmetro específico
    Z-score = (valor - média) / desvio padrão
    """
    if desvio_padrao == 0:
        return None
    
    return round((valor - media_populacional) / desvio_padrao, 2)

def interpretar_funcao_diastolica(parametros):
    """
    Interpreta a função diastólica baseada nos parâmetros disponíveis
    """
    interpretacao = {
        'grau': 'Normal',
        'descricao': 'Função diastólica preservada',
        'recomendacoes': []
    }
    
    try:
        # Algoritmo simplificado de classificação
        if parametros.relacao_e_a and parametros.relacao_e_e_linha:
            e_a = parametros.relacao_e_a
            e_e_linha = parametros.relacao_e_e_linha
            
            if e_a < 0.8 and e_e_linha < 8:
                interpretacao['grau'] = 'Disfunção Grau I'
                interpretacao['descricao'] = 'Alteração do relaxamento'
                
            elif 0.8 <= e_a <= 1.5 and 8 <= e_e_linha <= 13:
                interpretacao['grau'] = 'Indeterminado'
                interpretacao['descricao'] = 'Necessária avaliação adicional'
                
            elif e_a > 2 and e_e_linha > 14:
                interpretacao['grau'] = 'Disfunção Grau III'
                interpretacao['descricao'] = 'Padrão restritivo'
                interpretacao['recomendacoes'].append('Avaliação cardiológica urgente')
                
    except Exception as e:
        logger.warning(f"Erro na interpretação da função diastólica: {e}")
        
    return interpretacao

def calcular_risco_cardiovascular(parametros, fatores_risco=None):
    """
    Calcula pontuação de risco cardiovascular baseada nos parâmetros
    """
    pontuacao = 0
    fatores = []
    
    try:
        # Fração de ejeção reduzida
        if parametros.fracao_ejecao and parametros.fracao_ejecao < 50:
            pontuacao += 3
            fatores.append('Fração de ejeção reduzida')
        
        # Hipertrofia ventricular
        if parametros.indice_massa_ve:
            limite = 115  # Ajustar conforme sexo
            if parametros.indice_massa_ve > limite:
                pontuacao += 2
                fatores.append('Hipertrofia ventricular esquerda')
        
        # Disfunção diastólica
        if parametros.relacao_e_e_linha and parametros.relacao_e_e_linha > 14:
            pontuacao += 2
            fatores.append('Disfunção diastólica')
        
        # Dilatação atrial
        if parametros.relacao_atrio_esquerdo_aorta and parametros.relacao_atrio_esquerdo_aorta > 1.5:
            pontuacao += 1
            fatores.append('Dilatação do átrio esquerdo')
        
        # Hipertensão pulmonar
        if parametros.pressao_sistolica_vd and parametros.pressao_sistolica_vd > 35:
            pontuacao += 2
            fatores.append('Hipertensão pulmonar')
            
    except Exception as e:
        logger.warning(f"Erro no cálculo de risco cardiovascular: {e}")
    
    # Classificar risco
    if pontuacao <= 2:
        risco = 'Baixo'
    elif pontuacao <= 5:
        risco = 'Moderado'
    else:
        risco = 'Alto'
    
    return {
        'pontuacao': pontuacao,
        'risco': risco,
        'fatores': fatores
    }

# Funções utilitárias
def arredondar_valor(valor, casas_decimais=2):
    """Arredonda um valor para o número especificado de casas decimais"""
    if valor is None:
        return None
    return round(float(valor), casas_decimais)

def formatar_resultado(valor, unidade, casas_decimais=2):
    """Formata um resultado com sua unidade"""
    if valor is None:
        return "-"
    return f"{round(valor, casas_decimais)} {unidade}"

def validar_consistencia_parametros(parametros):
    """
    Valida a consistência entre diferentes parâmetros
    """
    inconsistencias = []
    
    try:
        # Verificar se DDVE > DSVE
        if (parametros.diametro_diastolico_final_ve and 
            parametros.diametro_sistolico_final and
            parametros.diametro_diastolico_final_ve <= parametros.diametro_sistolico_final):
            inconsistencias.append("DDVE deve ser maior que DSVE")
        
        # Verificar se VDF > VSF
        if (parametros.volume_diastolico_final and 
            parametros.volume_sistolico_final and
            parametros.volume_diastolico_final <= parametros.volume_sistolico_final):
            inconsistencias.append("Volume diastólico deve ser maior que volume sistólico")
        
        # Verificar fração de ejeção vs percentual de encurtamento
        if (parametros.fracao_ejecao and parametros.percentual_encurtamento):
            # Deve haver correlação aproximada
            fe_estimada = parametros.percentual_encurtamento * 2  # Aproximação grosseira
            if abs(parametros.fracao_ejecao - fe_estimada) > 20:
                inconsistencias.append("Possível inconsistência entre FE e % encurtamento")
                
    except Exception as e:
        logger.warning(f"Erro na validação de consistência: {e}")
    
    return inconsistencias
