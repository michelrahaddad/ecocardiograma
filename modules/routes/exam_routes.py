"""
Módulo de Rotas para Gerenciamento de Exames
Funcionalidades: criação, edição, visualização e exclusão de exames de ecocardiograma
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma, datetime_brasilia
from utils.logging_system import log_user_action, log_database_operation
import re
from datetime import datetime


def normalize_patient_name(nome: str) -> str:
    """
    Normaliza nome do paciente para verificação de duplicatas.
    
    Args:
        nome: Nome original do paciente
        
    Returns:
        Nome normalizado em lowercase, sem acentos e espaços extras
    """
    if not nome:
        return ""
    
    # Converter para minúsculas
    nome_normalizado = nome.lower().strip()
    
    # Remover acentos
    acentos = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'ñ': 'n'
    }
    
    for acento, sem_acento in acentos.items():
        nome_normalizado = nome_normalizado.replace(acento, sem_acento)
    
    # Remover espaços extras e caracteres especiais
    nome_normalizado = re.sub(r'\s+', ' ', nome_normalizado)
    nome_normalizado = re.sub(r'[^\w\s]', '', nome_normalizado)
    
    return nome_normalizado


def check_duplicate_patient(nome_paciente: str) -> dict:
    """
    Verifica se já existe paciente com nome similar.
    
    Args:
        nome_paciente: Nome a ser verificado
        
    Returns:
        Dict com informações sobre duplicatas encontradas
    """
    nome_normalizado = normalize_patient_name(nome_paciente)
    
    if not nome_normalizado:
        return {'has_duplicate': False, 'message': None}
    
    # Buscar exames com nomes similares
    exames_existentes = Exame.query.all()
    
    for exame in exames_existentes:
        nome_existente_normalizado = normalize_patient_name(exame.nome_paciente)
        
        if nome_existente_normalizado == nome_normalizado:
            return {
                'has_duplicate': True,
                'existing_name': exame.nome_paciente,
                'message': f'Paciente "{exame.nome_paciente}" já existe no sistema. Use o módulo Prontuário para adicionar novos exames.'
            }
    
    return {'has_duplicate': False, 'message': None}


def create_new_exam(form_data: dict) -> tuple:
    """
    Cria novo exame no sistema.
    
    Args:
        form_data: Dados do formulário
        
    Returns:
        Tuple com (success: bool, exam_id: int, message: str)
    """
    try:
        # Validar dados obrigatórios
        required_fields = ['nome_paciente', 'data_nascimento', 'idade', 'sexo', 'data_exame']
        for field in required_fields:
            if not form_data.get(field):
                return False, None, f'Campo obrigatório: {field}'
        
        # Comentado: Verificação de duplicatas removida para permitir múltiplos exames
        # duplicate_check = check_duplicate_patient(form_data['nome_paciente'])
        # if duplicate_check['has_duplicate']:
        #     return False, None, duplicate_check['message']
        
        # Criar novo exame
        novo_exame = Exame()
        novo_exame.nome_paciente = form_data['nome_paciente'].strip()
        novo_exame.data_nascimento = form_data['data_nascimento']
        novo_exame.idade = int(form_data['idade'])
        novo_exame.sexo = form_data['sexo']
        novo_exame.data_exame = form_data['data_exame']
        novo_exame.tipo_atendimento = form_data.get('tipo_atendimento', '').strip()
        novo_exame.medico_usuario = form_data.get('medico_usuario', '').strip()
        novo_exame.medico_solicitante = form_data.get('medico_solicitante', '').strip()
        novo_exame.indicacao = form_data.get('indicacao', '').strip()
        
        db.session.add(novo_exame)
        db.session.commit()
        
        # Log da operação
        log_database_operation(
            f'Novo exame criado',
            f'Paciente: {novo_exame.nome_paciente}, Data: {novo_exame.data_exame}',
            'CREATE',
            current_user.username if current_user.is_authenticated else 'System'
        )
        
        return True, novo_exame.id, 'Exame criado com sucesso'
        
    except ValueError as e:
        return False, None, f'Erro de validação: {str(e)}'
    except Exception as e:
        db.session.rollback()
        return False, None, f'Erro ao criar exame: {str(e)}'


def update_exam_parameters(exame_id: int, form_data: dict) -> tuple:
    """
    Atualiza parâmetros do ecocardiograma.
    
    Args:
        exame_id: ID do exame
        form_data: Dados do formulário
        
    Returns:
        Tuple com (success: bool, message: str)
    """
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        # Buscar ou criar parâmetros
        parametros = ParametrosEcocardiograma.query.filter_by(exame_id=exame_id).first()
        if not parametros:
            parametros = ParametrosEcocardiograma()
            parametros.exame_id = exame_id
            db.session.add(parametros)
        
        # Atualizar campos dos parâmetros
        parameter_fields = [
            'peso', 'altura', 'superficie_corporal', 'frequencia_cardiaca',
            'atrio_esquerdo', 'raiz_aorta', 'relacao_atrio_esquerdo_aorta',
            'aorta_ascendente', 'diametro_ventricular_direito', 'diametro_basal_vd',
            'diametro_diastolico_final_ve', 'diametro_sistolico_final',
            'percentual_encurtamento', 'espessura_diastolica_septo',
            'espessura_diastolica_ppve', 'relacao_septo_parede_posterior',
            'volume_diastolico_final', 'volume_sistolico_final',
            'volume_ejecao', 'fracao_ejecao', 'indice_massa_ve', 'massa_ve',
            'fluxo_pulmonar', 'fluxo_mitral', 'fluxo_aortico', 'fluxo_tricuspide',
            'gradiente_vd_ap', 'gradiente_ae_ve', 'gradiente_ve_ao', 'gradiente_ad_vd',
            'gradiente_tricuspide', 'pressao_sistolica_vd'
        ]
        
        for field in parameter_fields:
            if field in form_data and form_data[field]:
                try:
                    setattr(parametros, field, float(form_data[field]))
                except (ValueError, TypeError):
                    continue
        
        db.session.commit()
        
        log_database_operation(
            f'Parâmetros atualizados',
            f'Exame ID: {exame_id}, Paciente: {exame.nome_paciente}',
            'UPDATE',
            current_user.username if current_user.is_authenticated else 'System'
        )
        
        return True, 'Parâmetros salvos com sucesso'
        
    except Exception as e:
        db.session.rollback()
        return False, f'Erro ao salvar parâmetros: {str(e)}'


def update_exam_report(exame_id: int, form_data: dict) -> tuple:
    """
    Atualiza laudo do ecocardiograma.
    
    Args:
        exame_id: ID do exame
        form_data: Dados do formulário
        
    Returns:
        Tuple com (success: bool, message: str)
    """
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        # Buscar ou criar laudo
        laudo = LaudoEcocardiograma.query.filter_by(exame_id=exame_id).first()
        if not laudo:
            laudo = LaudoEcocardiograma()
            laudo.exame_id = exame_id
            db.session.add(laudo)
        
        # Atualizar campos do laudo
        report_fields = ['modo_m_bidimensional', 'doppler_convencional', 'doppler_tecidual', 'conclusao', 'recomendacoes']
        
        for field in report_fields:
            if field in form_data:
                setattr(laudo, field, form_data[field].strip() if form_data[field] else '')
        
        db.session.commit()
        
        log_database_operation(
            f'Laudo atualizado',
            f'Exame ID: {exame_id}, Paciente: {exame.nome_paciente}',
            'UPDATE',
            current_user.username if current_user.is_authenticated else 'System'
        )
        
        return True, 'Laudo salvo com sucesso'
        
    except Exception as e:
        db.session.rollback()
        return False, f'Erro ao salvar laudo: {str(e)}'


def delete_exam_safely(exame_id: int) -> tuple:
    """
    Remove exame do sistema com segurança.
    
    Args:
        exame_id: ID do exame a ser removido
        
    Returns:
        Tuple com (success: bool, message: str)
    """
    try:
        exame = Exame.query.get_or_404(exame_id)
        patient_name = exame.nome_paciente
        
        # Remover registros relacionados (cascade já configurado no modelo)
        db.session.delete(exame)
        db.session.commit()
        
        log_database_operation(
            f'Exame excluído',
            f'Paciente: {patient_name}, Data: {exame.data_exame}',
            'DELETE',
            current_user.username if current_user.is_authenticated else 'System'
        )
        
        return True, f'Exame do paciente {patient_name} excluído com sucesso'
        
    except Exception as e:
        db.session.rollback()
        return False, f'Erro ao excluir exame: {str(e)}'


def get_patient_exams(nome_paciente: str) -> list:
    """
    Busca todos os exames de um paciente específico.
    
    Args:
        nome_paciente: Nome do paciente
        
    Returns:
        Lista de exames ordenados por data decrescente
    """
    try:
        exames = Exame.query.filter_by(nome_paciente=nome_paciente).order_by(Exame.data_exame.desc()).all()
        return exames
    except Exception:
        return []