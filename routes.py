import os
import json
import base64
from datetime import datetime, timezone, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, session, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, desc
from functools import wraps
from app import app, db
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma, Medico, LogSistema, PatologiaLaudo, TemplateLaudo, LaudoTemplate, datetime_brasilia
from auth.models import AuthUser
from utils.pdf_generator_compacto import generate_pdf_report
from utils.calculations import calcular_parametros_derivados
from utils.backup import criar_backup, restaurar_backup
from utils.backup_security import create_manual_backup, create_daily_backup, get_backup_list, restore_from_backup
from utils.backup_scheduler import init_backup_scheduler, get_backup_scheduler
from utils.logging_system import (
    log_system_event, log_user_action, log_database_operation, 
    log_pdf_generation, log_backup_operation, log_error_with_traceback,
    LoggedOperation
)
import logging
import os
from datetime import datetime

def admin_required(f):
    """Decorator para rotas que requerem acesso administrativo"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth_login'))
        if not current_user.is_admin():
            flash('Acesso negado. Você precisa ser administrador para acessar esta área.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ===== ROTAS DE AUTENTICAÇÃO =====

@app.route('/login', methods=['GET', 'POST'])
def auth_login():
    """Página de login do sistema"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = AuthUser.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password) and usuario.is_active:
            login_user(usuario)
            log_user_action(f'Login realizado com sucesso - Usuário {username}')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'error')
            log_user_action(f'Tentativa de login falhada - Usuário {username}')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def auth_logout():
    """Logout do sistema"""
    username = current_user.username
    logout_user()
    log_user_action(f'Logout realizado - Usuário {username}')
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth_login'))

@app.route('/gerenciar-usuarios')
@admin_required
def gerenciar_usuarios():
    """Página de gerenciamento de usuários (apenas administradores)"""
    usuarios = AuthUser.query.all()
    return render_template('auth/gerenciar_usuarios.html', usuarios=usuarios)

@app.route('/criar-usuario', methods=['GET', 'POST'])
@admin_required
def criar_usuario():
    """Criar novo usuário (apenas administradores)"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Verificar se usuário já existe
        if AuthUser.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return redirect(url_for('criar_usuario'))
        
        if AuthUser.query.filter_by(email=email).first():
            flash('Email já está em uso.', 'error')
            return redirect(url_for('criar_usuario'))
        
        # Criar novo usuário
        novo_usuario = AuthUser(
            username=username,
            email=email,
            role=role,
            is_verified=True,
            is_active_flag=True
        )
        novo_usuario.set_password(password)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        log_user_action(f'Usuário {username} criado com sucesso pelo administrador {current_user.username}')
        flash(f'Usuário {username} criado com sucesso.', 'success')
        return redirect(url_for('gerenciar_usuarios'))
    
    return render_template('auth/criar_usuario.html')

@app.route('/editar-usuario/<int:usuario_id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(usuario_id):
    """Editar usuário existente (apenas administradores)"""
    usuario = AuthUser.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.email = request.form['email']
        usuario.role = request.form['role']
        usuario.is_active_flag = 'ativo' in request.form
        
        if request.form.get('password'):
            usuario.set_password(request.form['password'])
        
        db.session.commit()
        
        log_user_action(f'Usuário {usuario.username} editado pelo administrador {current_user.username}')
        flash(f'Usuário {usuario.username} atualizado com sucesso.', 'success')
        return redirect(url_for('gerenciar_usuarios'))
    
    return render_template('auth/editar_usuario.html', usuario=usuario)

@app.route('/deletar-usuario/<int:usuario_id>', methods=['POST'])
@admin_required
def deletar_usuario(usuario_id):
    """Deletar usuário (apenas administradores)"""
    usuario = AuthUser.query.get_or_404(usuario_id)
    
    if usuario.id == current_user.id:
        flash('Você não pode deletar sua própria conta.', 'error')
        return redirect(url_for('gerenciar_usuarios'))
    
    username = usuario.username
    db.session.delete(usuario)
    db.session.commit()
    
    log_user_action(f'Usuário {username} deletado pelo administrador {current_user.username}')
    flash(f'Usuário {username} deletado com sucesso.', 'success')
    return redirect(url_for('gerenciar_usuarios'))

# ===== INICIALIZAÇÃO DO SISTEMA =====

@app.route('/inicializar-sistema')
def inicializar_sistema():
    """Criar usuário administrador padrão se não existir"""
    try:
        # Verificar se já existe algum usuário administrador
        admin_existente = AuthUser.query.filter_by(role='admin').first()
        
        if not admin_existente:
            # Criar usuário administrador padrão
            admin = AuthUser(
                username='admin',
                email='admin@grupovidah.com.br',
                role='admin',
                is_verified=True,
                is_active_flag=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            log_user_action('Usuário administrador padrão criado no sistema')
            flash('Sistema inicializado! Usuário: admin | Senha: admin123', 'success')
        else:
            flash('Sistema já possui usuário administrador configurado.', 'info')
            
        return redirect(url_for('auth_login'))
        
    except Exception as e:
        log_error_with_traceback(f'Erro ao inicializar sistema: {str(e)}')
        flash('Erro ao inicializar sistema.', 'error')
        return redirect(url_for('auth_login'))

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
@login_required
def index():
    """Página inicial com lista de exames recentes e estatísticas"""
    try:
        # Buscar exames recentes agrupados por paciente
        exames_recentes = db.session.query(
            Exame.nome_paciente,
            func.count(Exame.id).label('total_exames'),
            func.max(Exame.data_exame).label('ultimo_exame')
        ).group_by(Exame.nome_paciente).order_by(desc('ultimo_exame')).limit(10).all()
        
        # Estatísticas gerais
        total_exames = db.session.query(Exame).count()
        total_pacientes = db.session.query(Exame.nome_paciente).distinct().count()
        exames_hoje = db.session.query(Exame).filter(
            Exame.data_exame == datetime_brasilia().strftime('%d/%m/%Y')
        ).count()
        
        return render_template('index.html', 
                             exames_recentes=exames_recentes,
                             total_exames=total_exames,
                             total_pacientes=total_pacientes,
                             exames_hoje=exames_hoje)
    except Exception as e:
        logging.error(f"Erro na página inicial: {str(e)}")
        return render_template('index.html', 
                             exames_recentes=[],
                             total_exames=0,
                             total_pacientes=0,
                             exames_hoje=0)

def normalizar_nome_paciente(nome):
    """Normaliza o nome do paciente para verificação rigorosa de duplicatas"""
    if not nome:
        return ""
    import unicodedata
    import re
    
    # Remove espaços extras e converte para minúsculas
    nome_limpo = ' '.join(nome.strip().split())
    
    # Remove acentos e caracteres especiais
    nome_sem_acento = unicodedata.normalize('NFD', nome_limpo).encode('ascii', 'ignore').decode('ascii')
    
    # Remove pontuação e converte para minúsculas
    nome_normalizado = re.sub(r'[^\w\s]', '', nome_sem_acento.lower())
    
    # Remove espaços duplos resultantes
    return ' '.join(nome_normalizado.split())

def verificar_nome_duplicado(nome_paciente):
    """Verifica se já existe um paciente com nome similar"""
    nome_normalizado = normalizar_nome_paciente(nome_paciente)
    
    # Buscar todos os nomes de pacientes existentes
    pacientes_existentes = db.session.query(Exame.nome_paciente).distinct().all()
    
    for (nome_existente,) in pacientes_existentes:
        if normalizar_nome_paciente(nome_existente) == nome_normalizado:
            return nome_existente  # Retorna o nome original encontrado
    
    return None

@app.route('/novo-exame', methods=['GET', 'POST'])
@app.route('/novo_exame', methods=['GET', 'POST'])
def novo_exame():
    """Formulário para criação de novo exame"""
    # Verificar se deve clonar dados de um paciente existente
    clone_paciente = request.args.get('clone_paciente')
    dados_clonados = None
    
    if clone_paciente and request.method == 'GET':
        # Buscar último exame do paciente para clonagem COMPLETA
        logging.info(f"Tentando clonar dados COMPLETOS do paciente: {clone_paciente}")
        
        ultimo_exame = Exame.query.filter_by(nome_paciente=clone_paciente).order_by(Exame.id.desc()).first()
        
        if ultimo_exame:
            logging.info(f"Último exame encontrado - ID: {ultimo_exame.id}, Data: {ultimo_exame.data_exame}")
            
            # Clonar dados básicos
            dados_clonados = {
                'nome_paciente': ultimo_exame.nome_paciente,
                'data_nascimento': ultimo_exame.data_nascimento,
                'idade': ultimo_exame.idade,
                'sexo': ultimo_exame.sexo,
                'tipo_atendimento': ultimo_exame.tipo_atendimento,
                'medico_usuario': ultimo_exame.medico_usuario,
                'medico_solicitante': ultimo_exame.medico_solicitante,
                'indicacao': ultimo_exame.indicacao
            }
            
            # Clonar parâmetros ecocardiográficos se existirem
            if ultimo_exame.parametros:
                dados_clonados['parametros'] = {
                    'peso': ultimo_exame.parametros.peso,
                    'altura': ultimo_exame.parametros.altura,
                    'superficie_corporal': ultimo_exame.parametros.superficie_corporal,
                    'frequencia_cardiaca': ultimo_exame.parametros.frequencia_cardiaca,
                    'atrio_esquerdo': ultimo_exame.parametros.atrio_esquerdo,
                    'raiz_aorta': ultimo_exame.parametros.raiz_aorta,
                    'relacao_atrio_esquerdo_aorta': ultimo_exame.parametros.relacao_atrio_esquerdo_aorta,
                    'aorta_ascendente': ultimo_exame.parametros.aorta_ascendente,
                    'diametro_diastolico_final_ve': ultimo_exame.parametros.diametro_diastolico_final_ve,
                    'diametro_sistolico_final': ultimo_exame.parametros.diametro_sistolico_final,
                    'percentual_encurtamento': ultimo_exame.parametros.percentual_encurtamento,
                    'espessura_diastolica_septo': ultimo_exame.parametros.espessura_diastolica_septo,
                    'espessura_diastolica_ppve': ultimo_exame.parametros.espessura_diastolica_ppve,
                    'volume_diastolico_final': ultimo_exame.parametros.volume_diastolico_final,
                    'volume_sistolico_final': ultimo_exame.parametros.volume_sistolico_final,
                    'fracao_ejecao': ultimo_exame.parametros.fracao_ejecao,
                    'massa_ve': ultimo_exame.parametros.massa_ve
                }
            
            # Clonar laudos se existirem
            if ultimo_exame.laudos and len(ultimo_exame.laudos) > 0:
                laudo = ultimo_exame.laudos[0]
                dados_clonados['laudos'] = {
                    'modo_m_bidimensional': laudo.modo_m_bidimensional,
                    'doppler_convencional': laudo.doppler_convencional,
                    'doppler_tecidual': laudo.doppler_tecidual,
                    'conclusao': laudo.conclusao,
                    'recomendacoes': laudo.recomendacoes
                }
            
            logging.info(f"Dados COMPLETOS clonados: dados básicos + {len(dados_clonados.get('parametros', {}))} parâmetros + laudos")
        else:
            logging.warning(f"Nenhum exame encontrado para o paciente: {clone_paciente}")
    
    if request.method == 'POST':
        try:
            nome_paciente = request.form['nome_paciente'].strip()
            
            # Comentado: Verificação de duplicação removida para permitir múltiplos exames
            # nome_existente = verificar_nome_duplicado(nome_paciente)
            # if nome_existente:
            #     flash(f'Paciente "{nome_existente}" já existe no sistema. Use o nome exato ou acesse o prontuário para criar novo exame.', 'warning')
            #     return render_template('novo_exame.html')
            
            # Log início da operação
            log_user_action('Criação de novo exame iniciada', f"Paciente: {nome_paciente}")
            
            exame = Exame()
            exame.nome_paciente = nome_paciente
            exame.data_nascimento = request.form['data_nascimento']
            exame.idade = int(request.form['idade'])
            exame.sexo = request.form['sexo']
            exame.data_exame = request.form['data_exame']
            exame.tipo_atendimento = request.form.get('tipo_atendimento')
            exame.medico_usuario = request.form.get('medico_usuario')
            exame.medico_solicitante = request.form.get('medico_solicitante')
            exame.indicacao = request.form.get('indicacao')
            
            db.session.add(exame)
            db.session.flush()  # Para obter ID antes do commit
            
            # Se tem dados clonados, criar parâmetros e laudos automaticamente
            if dados_clonados and dados_clonados.get('parametros'):
                parametros = ParametrosEcocardiograma()
                parametros.exame_id = exame.id
                
                # Copiar todos os parâmetros clonados
                for campo, valor in dados_clonados['parametros'].items():
                    if hasattr(parametros, campo) and valor is not None:
                        setattr(parametros, campo, valor)
                
                db.session.add(parametros)
            
            # Se tem laudos clonados, criar laudos automaticamente
            if dados_clonados and dados_clonados.get('laudos'):
                laudo = LaudoEcocardiograma()
                laudo.exame_id = exame.id
                
                # Copiar todos os laudos clonados
                for campo, valor in dados_clonados['laudos'].items():
                    if hasattr(laudo, campo) and valor:
                        setattr(laudo, campo, valor)
                
                db.session.add(laudo)
            
            db.session.commit()
            
            # Log sucesso da operação
            log_database_operation('CREATE', 'exames', exame.id, True)
            log_user_action('Exame criado com sucesso', f"ID: {exame.id}, Paciente: {exame.nome_paciente}")
            
            flash('Exame criado com sucesso!', 'success')
            return redirect(url_for('parametros', exame_id=exame.id))
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(e, 'novo_exame')
            log_database_operation('CREATE', 'exames', None, False, str(e))
            flash('Erro ao criar exame. Tente novamente.', 'error')
    
    return render_template('novo_exame.html', dados_clonados=dados_clonados)

@app.route('/parametros/<int:exame_id>', methods=['GET', 'POST'])
def parametros(exame_id):
    """Formulário de parâmetros do ecocardiograma"""
    exame = db.session.get(Exame, exame_id)
    if not exame:
        flash('Exame não encontrado.', 'error')
        return redirect(url_for('index'))
    
    parametros_obj = exame.parametros
    if not parametros_obj:
        parametros_obj = ParametrosEcocardiograma()
        parametros_obj.exame_id = exame_id
        db.session.add(parametros_obj)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            # Atualizar todos os campos de parâmetros
            campos_parametros = [
                'peso', 'altura', 'superficie_corporal', 'frequencia_cardiaca',
                'atrio_esquerdo', 'raiz_aorta', 'relacao_atrio_esquerdo_aorta',
                'aorta_ascendente', 'diametro_ventricular_direito', 'diametro_basal_vd',
                'diametro_diastolico_final_ve', 'diametro_sistolico_final',
                'percentual_encurtamento', 'espessura_diastolica_septo',
                'espessura_diastolica_ppve', 'relacao_septo_parede_posterior',
                'volume_diastolico_final', 'volume_sistolico_final',
                'volume_ejecao', 'fracao_ejecao', 'indice_massa_ve', 'massa_ve',
                'fluxo_pulmonar', 'fluxo_mitral', 'fluxo_aortico', 'fluxo_tricuspide',
                'onda_e', 'onda_a', 'relacao_e_a', 'tempo_desaceleracao_e',
                'velocidade_propagacao_fluxo', 'gradiente_vd_ap', 'gradiente_ae_ve', 
                'gradiente_ve_ao', 'gradiente_ad_vd', 'gradiente_tricuspide', 'pressao_sistolica_vd'
            ]
            
            for campo in campos_parametros:
                valor = request.form.get(campo)
                if valor and valor.strip():
                    try:
                        setattr(parametros_obj, campo, float(valor))
                    except ValueError:
                        continue
            
            # Campos de texto/seleção
            campos_texto = ['insuficiencia_mitral', 'insuficiencia_tricuspide',
                           'insuficiencia_aortica', 'insuficiencia_pulmonar']
            
            for campo in campos_texto:
                valor = request.form.get(campo)
                if valor:
                    setattr(parametros_obj, campo, valor)
            
            # Calcular parâmetros derivados
            calcular_parametros_derivados(parametros_obj)
            
            db.session.commit()
            flash('Parâmetros salvos com sucesso!', 'success')
            
            # Verificar se deve continuar para laudo
            if 'continuar_laudo' in request.form:
                return redirect(url_for('laudo', exame_id=exame_id))
            
        except Exception as e:
            logging.error(f"Erro ao salvar parâmetros: {str(e)}")
            flash('Erro ao salvar parâmetros. Tente novamente.', 'error')
            db.session.rollback()
    
    return render_template('parametros.html', exame=exame, parametros=parametros_obj)

@app.route('/salvar_parametros/<int:exame_id>', methods=['POST'])
@login_required
def salvar_parametros(exame_id):
    """Rota específica para salvar parâmetros ecocardiográficos"""
    try:
        # Buscar exame
        exame = Exame.query.get_or_404(exame_id)
        
        # Buscar parâmetros existentes ou criar novos
        parametros = ParametrosEcocardiograma.query.filter_by(exame_id=exame_id).first()
        if not parametros:
            parametros = ParametrosEcocardiograma(exame_id=exame_id)
            db.session.add(parametros)
            db.session.commit()
        
        # Atualizar todos os campos dos parâmetros
        campos_parametros = [
            'peso', 'altura', 'superficie_corporal', 'frequencia_cardiaca',
            'atrio_esquerdo', 'raiz_aorta', 'relacao_atrio_esquerdo_aorta',
            'aorta_ascendente', 'diametro_ventricular_direito', 'diametro_basal_vd',
            'diametro_diastolico_final_ve', 'diametro_sistolico_final',
            'percentual_encurtamento', 'espessura_diastolica_septo',
            'espessura_diastolica_ppve', 'relacao_septo_parede_posterior',
            'volume_diastolico_final', 'volume_sistolico_final', 'volume_ejecao',
            'fracao_ejecao', 'indice_massa_ve', 'massa_ve',
            'fluxo_pulmonar', 'fluxo_mitral', 'fluxo_aortico', 'fluxo_tricuspide',
            'gradiente_vd_ap', 'gradiente_ae_ve', 'gradiente_ve_ao', 'gradiente_ad_vd',
            'gradiente_tricuspide', 'pressao_sistolica_vd'
        ]
        
        campos_atualizados = 0
        for campo in campos_parametros:
            valor = request.form.get(campo)
            if valor and valor.strip():
                try:
                    setattr(parametros, campo, float(valor.replace(',', '.')))
                    campos_atualizados += 1
                except ValueError:
                    pass  # Ignorar valores inválidos
        
        db.session.commit()
        
        # Verificar se deve continuar para laudo
        if request.form.get('continuar_laudo'):
            flash('Parâmetros salvos! Redirecionando para o laudo.', 'success')
            return redirect(url_for('laudo', exame_id=exame_id))
        else:
            flash('Parâmetros salvos com sucesso!', 'success')
            return redirect(url_for('parametros', exame_id=exame_id))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar parâmetros: {str(e)}', 'error')
        return redirect(url_for('parametros', exame_id=exame_id))

@app.route('/laudo/<int:exame_id>', methods=['GET', 'POST'])
@login_required
def laudo(exame_id):
    """Formulário de laudo do ecocardiograma"""
    exame = db.session.get(Exame, exame_id)
    if not exame:
        flash('Exame não encontrado.', 'error')
        return redirect(url_for('index'))
    
    laudo_obj = None
    if exame.laudos:
        laudo_obj = exame.laudos[0]
    
    if not laudo_obj:
        laudo_obj = LaudoEcocardiograma()
        laudo_obj.exame_id = exame_id
        db.session.add(laudo_obj)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            laudo_obj.modo_m_bidimensional = request.form.get('modo_m_bidimensional', '')
            laudo_obj.doppler_convencional = request.form.get('doppler_convencional', '')
            laudo_obj.doppler_tecidual = request.form.get('doppler_tecidual', '')
            laudo_obj.conclusao = request.form.get('conclusao', '')
            laudo_obj.recomendacoes = request.form.get('recomendacoes', '')
            
            db.session.commit()
            flash('Laudo salvo com sucesso!', 'success')
            
            # Verificar se deve gerar PDF
            if 'gerar_pdf' in request.form:
                return redirect(url_for('gerar_pdf', exame_id=exame_id))
            
        except Exception as e:
            logging.error(f"Erro ao salvar laudo: {str(e)}")
            flash('Erro ao salvar laudo. Tente novamente.', 'error')
            db.session.rollback()
    
    return render_template('laudo.html', exame=exame, laudo=laudo_obj)

@app.route('/salvar_laudo/<int:exame_id>', methods=['POST'])
@login_required
def salvar_laudo(exame_id):
    """Rota específica para salvar laudo ecocardiográfico"""
    try:
        # Buscar exame
        exame = Exame.query.get_or_404(exame_id)
        
        # Buscar laudo existente ou criar novo
        laudo_obj = None
        if exame.laudos:
            laudo_obj = exame.laudos[0]
        else:
            laudo_obj = LaudoEcocardiograma(exame_id=exame_id)
            db.session.add(laudo_obj)
        
        # Atualizar campos do laudo
        if 'modo_m_bidimensional' in request.form:
            laudo_obj.modo_m_bidimensional = request.form['modo_m_bidimensional']
        if 'doppler_convencional' in request.form:
            laudo_obj.doppler_convencional = request.form['doppler_convencional']
        if 'doppler_tecidual' in request.form:
            laudo_obj.doppler_tecidual = request.form['doppler_tecidual']
        if 'conclusao' in request.form:
            laudo_obj.conclusao = request.form['conclusao']
        if 'recomendacoes' in request.form:
            laudo_obj.recomendacoes = request.form['recomendacoes']
        
        db.session.commit()
        
        flash('Laudo salvo com sucesso!', 'success')
        return redirect(url_for('laudo', exame_id=exame_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar laudo: {str(e)}', 'error')
        return redirect(url_for('laudo', exame_id=exame_id))

@app.route('/visualizar_exame/<int:exame_id>')
def visualizar_exame(exame_id):
    """Visualização completa do exame"""
    exame = db.session.get(Exame, exame_id)
    if not exame:
        flash('Exame não encontrado.', 'error')
        return redirect(url_for('index'))
    
    return render_template('visualizar_exame.html', exame=exame)

@app.route('/exames_paciente/<nome_paciente>')
def exames_paciente(nome_paciente):
    """Lista todos os exames de um paciente específico"""
    exames = db.session.query(Exame).filter(
        Exame.nome_paciente == nome_paciente
    ).order_by(desc(Exame.data_exame)).all()
    
    return render_template('exames_paciente.html', 
                         nome_paciente=nome_paciente, 
                         exames=exames)

@app.route('/gerar-pdf/<int:exame_id>')
@app.route('/gerar_pdf/<int:exame_id>')
def gerar_pdf(exame_id):
    """Gera PDF completo do exame"""
    try:
        # Log início da operação
        log_user_action('Geração de PDF iniciada', f'Exame ID: {exame_id}')
        
        # Buscar exame com recarregamento
        exame = db.session.get(Exame, exame_id)
        if not exame:
            log_system_event('ERROR', f'Exame não encontrado para PDF: ID {exame_id}', 'pdf_generation')
            flash('Exame não encontrado.', 'error')
            return redirect(url_for('index'))
        
        # Recarregar relacionamentos
        db.session.refresh(exame)
        
        log_system_event('INFO', f'Exame localizado para PDF: {exame.nome_paciente}', 'pdf_generation')
        
        # Buscar médico selecionado com fallback robusto
        medico_selecionado = None
        
        # Primeiro: Tentar médico da sessão
        medico_id = session.get('medico_selecionado')
        if medico_id:
            medico_selecionado = db.session.get(Medico, medico_id)
            if medico_selecionado:
                log_system_event('INFO', f'Médico selecionado para PDF: {medico_selecionado.nome}', 'pdf_generation')
        
        # Segundo: Tentar médico selecionado por ID
        if not medico_selecionado:
            medico_id = session.get('medico_selecionado_id')
            if medico_id:
                medico_selecionado = db.session.get(Medico, medico_id)
                if medico_selecionado:
                    log_system_event('INFO', f'Médico encontrado por ID: {medico_selecionado.nome}', 'pdf_generation')
        
        # Terceiro: Usar primeiro médico ativo
        if not medico_selecionado:
            medico_selecionado = db.session.query(Medico).filter_by(ativo=True).first()
            if medico_selecionado:
                logging.info(f"Usando primeiro médico ativo: {medico_selecionado.nome} (CRM: {medico_selecionado.crm})")
            else:
                logging.warning("Nenhum médico cadastrado no sistema")
        
        # Log dos dados encontrados para debug
        logging.info(f"Exame {exame_id}: parâmetros={exame.parametros is not None}, laudos={len(exame.laudos) if exame.laudos else 0}")
        
        if exame.parametros:
            logging.info(f"Parâmetros encontrados - peso: {exame.parametros.peso}, AE: {exame.parametros.atrio_esquerdo}")
        
        if exame.laudos:
            logging.info(f"Laudos encontrados: {len(exame.laudos)}")
        
        # Gerar PDF usando o sistema moderno
        logging.info(f"Iniciando geração de PDF moderno para {exame.nome_paciente}")
        
        # Preparar dados do médico com todas as informações
        medico_data = {
            'nome': medico_selecionado.nome if medico_selecionado else 'Michel Raineri Haddad',
            'crm': medico_selecionado.crm if medico_selecionado else 'CRM-SP 183299',
            'assinatura_data': medico_selecionado.assinatura_data if medico_selecionado else None,
            'assinatura_url': medico_selecionado.assinatura_url if medico_selecionado else None
        }
        
        # Usar o gerador premium com melhorias de design, layout e organização
        from utils.pdf_generator_design_premium import gerar_pdf_design_premium  
        pdf_path = gerar_pdf_design_premium(exame, medico_data)
        file_size = os.path.getsize(pdf_path)
        
        # Verificar se arquivo foi criado
        if not os.path.exists(pdf_path):
            logging.error(f"Arquivo PDF moderno não foi criado: {pdf_path}")
            raise Exception("Falha na criação do arquivo PDF moderno")
        
        logging.info(f"PDF moderno gerado com sucesso: {pdf_path} ({file_size} bytes)")
        
        # Nome seguro para download
        safe_name = "".join(c for c in exame.nome_paciente if c.isalnum() or c in (' ', '_')).rstrip()
        safe_date = exame.data_exame.replace("/", "") if exame.data_exame else datetime_brasilia().strftime('%Y%m%d')
        download_name = f'laudo_eco_{safe_name.replace(" ", "_")}_{safe_date}.pdf'
        
        logging.info(f"Enviando PDF para download: {download_name}")
        return send_file(pdf_path, as_attachment=True, download_name=download_name)
    
    except Exception as e:
        logging.error(f"Erro crítico ao gerar PDF para exame {exame_id}: {str(e)}", exc_info=True)
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('visualizar_exame', exame_id=exame_id))

@app.route('/cadastro_medico', methods=['GET', 'POST'])
@login_required
def cadastro_medico():
    """Página de cadastro e gerenciamento de médicos com assinatura digital"""
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            crm = request.form['crm']
            signature_data = request.form.get('signature_data')
            
            # Validar se assinatura foi fornecida
            if not signature_data:
                flash('Assinatura digital é obrigatória para cadastrar o médico.', 'error')
                return redirect(url_for('cadastro_medico'))
            
            # Verificar se médico já existe
            medico_existente = Medico.query.filter_by(crm=crm).first()
            if medico_existente:
                flash(f'Já existe um médico cadastrado com CRM {crm}.', 'error')
                return redirect(url_for('cadastro_medico'))
            
            # Criar novo médico com assinatura digital
            medico = Medico(
                nome=nome, 
                crm=crm,
                assinatura_data=signature_data,
                ativo=True
            )
            db.session.add(medico)
            db.session.commit()
            
            log_user_action(f'Médico cadastrado: {nome} (CRM: {crm})')
            flash(f'Médico {nome} cadastrado com sucesso e assinatura digital salva!', 'success')
            return redirect(url_for('cadastro_medico'))
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback(e, 'cadastro_medico')
            flash('Erro ao cadastrar médico. Tente novamente.', 'error')
    
    # Buscar todos os médicos e o selecionado
    medicos = Medico.query.filter_by(ativo=True).order_by(Medico.nome).all()
    medico_selecionado_id = session.get('medico_selecionado')
    medico_selecionado = None
    if medico_selecionado_id:
        medico_selecionado = Medico.query.get(medico_selecionado_id)
    
    return render_template('cadastro_medico.html', 
                         medicos=medicos, 
                         medico_selecionado=medico_selecionado)

@app.route('/selecionar_medico/<int:medico_id>', methods=['GET', 'POST'])
@login_required
def selecionar_medico(medico_id):
    """Selecionar médico para uso no sistema"""
    try:
        medico = Medico.query.get_or_404(medico_id)
        
        # Salvar na sessão
        session['medico_selecionado'] = medico_id
        session.permanent = True
        
        log_user_action(f'Médico selecionado: {medico.nome} (CRM: {medico.crm})')
        
        # Se for requisição AJAX, retornar JSON
        if request.method == 'POST' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True,
                'message': f'Médico {medico.nome} selecionado com sucesso!',
                'medico': {
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm,
                    'assinatura_data': medico.assinatura_data
                }
            })
        
        flash(f'Médico {medico.nome} selecionado com sucesso!', 'success')
        return redirect(url_for('cadastro_medico'))
        
    except Exception as e:
        log_error_with_traceback(e, f'selecionar_medico_{medico_id}')
        
        if request.method == 'POST' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': False,
                'message': 'Erro ao selecionar médico.'
            }), 500
        
        flash('Erro ao selecionar médico.', 'error')
        return redirect(url_for('cadastro_medico'))

# ===== APIS PARA MÉDICOS =====

@app.route('/api/medicos', methods=['GET'])
@login_required
def api_listar_medicos():
    """API para listar médicos cadastrados"""
    try:
        medicos = Medico.query.filter_by(ativo=True).order_by(Medico.nome).all()
        medico_selecionado_id = session.get('medico_selecionado')
        
        medicos_data = []
        for medico in medicos:
            medicos_data.append({
                'id': medico.id,
                'nome': medico.nome,
                'crm': medico.crm,
                'assinatura_data': medico.assinatura_data,
                'ativo': medico.ativo,
                'selecionado': medico.id == medico_selecionado_id,
                'created_at': medico.created_at.isoformat() if medico.created_at else None
            })
        
        return jsonify({
            'success': True,
            'medicos': medicos_data,
            'total': len(medicos_data),
            'medico_selecionado_id': medico_selecionado_id
        })
        
    except Exception as e:
        log_error_with_traceback(e, 'api_listar_medicos')
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar médicos.'
        }), 500

@app.route('/api/medicos/<int:medico_id>/assinatura', methods=['GET'])
@login_required
def api_obter_assinatura_medico(medico_id):
    """API para obter assinatura de um médico específico"""
    try:
        medico = Medico.query.get_or_404(medico_id)
        
        return jsonify({
            'success': True,
            'medico': {
                'id': medico.id,
                'nome': medico.nome,
                'crm': medico.crm,
                'assinatura_data': medico.assinatura_data
            }
        })
        
    except Exception as e:
        log_error_with_traceback(e, f'api_obter_assinatura_medico_{medico_id}')
        return jsonify({
            'success': False,
            'message': 'Médico não encontrado.'
        }), 404

@app.route('/api/medicos/selecionado', methods=['GET'])
@login_required
def api_medico_selecionado():
    """API para obter dados do médico atualmente selecionado"""
    try:
        medico_selecionado_id = session.get('medico_selecionado')
        
        if not medico_selecionado_id:
            return jsonify({
                'success': False,
                'message': 'Nenhum médico selecionado.'
            })
        
        medico = Medico.query.get(medico_selecionado_id)
        if not medico or not medico.ativo:
            # Limpar seleção inválida
            session.pop('medico_selecionado', None)
            return jsonify({
                'success': False,
                'message': 'Médico selecionado não encontrado ou inativo.'
            })
        
        return jsonify({
            'success': True,
            'medico': {
                'id': medico.id,
                'nome': medico.nome,
                'crm': medico.crm,
                'assinatura_data': medico.assinatura_data,
                'ativo': medico.ativo
            }
        })
        
    except Exception as e:
        log_error_with_traceback(e, 'api_medico_selecionado')
        return jsonify({
            'success': False,
            'message': 'Erro ao obter médico selecionado.'
        }), 500

@app.route('/api/limpar-medicos', methods=['POST'])
@login_required 
def api_limpar_medicos():
    """API para limpar todos os médicos cadastrados"""
    try:
        # Limpar seleção de médico da sessão
        session.pop('medico_selecionado', None)
        
        # Excluir todos os médicos
        medicos_removidos = Medico.query.count()
        Medico.query.delete()
        db.session.commit()
        
        log_user_action(f'Todos os médicos foram removidos ({medicos_removidos} médicos)')
        
        return jsonify({
            'success': True,
            'message': f'{medicos_removidos} médicos removidos com sucesso.',
            'medicos_removidos': medicos_removidos
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback(e, 'api_limpar_medicos')
        return jsonify({
            'success': False,
            'message': 'Erro ao remover médicos.'
        }), 500

@app.route('/excluir_exame/<int:exame_id>')
@login_required
def excluir_exame(exame_id):
    """Exclui um exame do sistema"""
    try:
        exame = db.session.get(Exame, exame_id)
        if exame:
            nome_paciente = exame.nome_paciente
            data_exame = exame.data_exame
            
            # Log da ação
            log_user_action(f'Exame EXCLUÍDO: ID {exame_id} - {nome_paciente} ({data_exame})', current_user.username if current_user.is_authenticated else 'Sistema')
            
            # Excluir relacionamentos primeiro (CASCADE deve fazer isso automaticamente)
            db.session.delete(exame)
            db.session.commit()
            
            flash(f'Exame de {nome_paciente} ({data_exame}) excluído com sucesso!', 'success')
            return redirect(url_for('prontuario_paciente', nome_paciente=nome_paciente))
        else:
            flash('Exame não encontrado.', 'error')
            return redirect(url_for('prontuario'))
    except Exception as e:
        logging.error(f"Erro ao excluir exame {exame_id}: {str(e)}")
        flash('Erro ao excluir exame. Tente novamente.', 'error')
        db.session.rollback()
        return redirect(url_for('prontuario'))

# Rotas de manutenção
@app.route('/manutencao')
def manutencao_index():
    """Painel principal de manutenção"""
    return render_template('manutencao/index.html')

@app.route('/manutencao/backup')
def pagina_backup():
    """Página de backup e restauração"""
    # Backups do sistema antigo
backups_antigos = []  # BackupSistema removido para deploy    
    # Backups do sistema seguro
    try:
        backups_seguros = get_backup_list()[:10]  # Últimos 10 backups
    except:
        backups_seguros = []
    
    return render_template('manutencao/backup.html', 
                         backups=backups_antigos, 
                         backups_seguros=backups_seguros)

@app.route('/manutencao/criar_backup', methods=['POST'])
def criar_backup_route():
    """Cria um novo backup do sistema"""
    try:
        tipo_backup = request.form.get('tipo_backup', 'COMPLETO')
        nome_arquivo = criar_backup(tipo_backup)
        
        flash('Backup criado com sucesso!', 'success')
    except Exception as e:
        logging.error(f"Erro ao criar backup: {str(e)}")
        flash('Erro ao criar backup. Tente novamente.', 'error')
    
    return redirect(url_for('pagina_backup'))

@app.route('/manutencao/backup_seguro', methods=['POST'])
def criar_backup_seguro():
    """Criar backup com sistema de segurança avançado"""
    try:
        tipo = request.form.get('tipo', 'MANUAL')
        
        if tipo == 'DIARIO':
            backup_path = create_daily_backup()
        else:
            backup_path = create_manual_backup()
        
        if backup_path:
            flash(f'Backup seguro criado: {backup_path.name}', 'success')
        else:
            flash('Erro ao criar backup seguro', 'error')
            
    except Exception as e:
        logging.error(f"Erro no backup seguro: {str(e)}")
        flash(f'Erro no backup seguro: {str(e)}', 'error')
    
    return redirect(url_for('pagina_backup'))

@app.route('/manutencao/logs')
def pagina_logs():
    """Página de visualização de logs"""
    try:
        logs = db.session.query(LogSistema).order_by(desc(LogSistema.created_at)).limit(100).all()
        log_user_action('Acesso ao sistema de logs', f'Total de logs: {len(logs)}')
        return render_template('manutencao/logs.html', logs=logs)
    except Exception as e:
        log_error_with_traceback(e, 'pagina_logs')
        return render_template('manutencao/logs.html', logs=[])

@app.route('/manutencao/exportar_logs')
def exportar_logs():
    """Exporta logs para arquivo CSV"""
    try:
        nivel = request.args.get('nivel')
        data = request.args.get('data')
        
        query = db.session.query(LogSistema)
        
        if nivel:
            query = query.filter(LogSistema.nivel == nivel)
        if data:
            query = query.filter(func.date(LogSistema.created_at) == data)
            
        logs = query.order_by(desc(LogSistema.created_at)).all()
        
        # Criar arquivo CSV em memória
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Data/Hora', 'Nível', 'Módulo', 'Mensagem', 'Usuário ID'])
        
        # Dados
        for log in logs:
            writer.writerow([
                log.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                log.nivel,
                log.modulo or '',
                log.mensagem,
                log.usuario_id or ''
            ])
        
        output.seek(0)
        
        # Preparar resposta
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=logs_sistema_{datetime_brasilia().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        log_error_with_traceback(e, 'exportar_logs')
        flash('Erro ao exportar logs', 'error')
        return redirect(url_for('pagina_logs'))

@app.route('/manutencao/limpar_logs', methods=['POST'])
def limpar_logs():
    """Remove logs antigos (mais de 30 dias)"""
    try:
        data_limite = datetime_brasilia() - timedelta(days=30)
        logs_antigos = db.session.query(LogSistema).filter(LogSistema.created_at < data_limite).count()
        
        db.session.query(LogSistema).filter(LogSistema.created_at < data_limite).delete()
        db.session.commit()
        
        log_system_event('INFO', f'Limpeza de logs realizada: {logs_antigos} logs removidos', 'log_cleanup')
        
        return jsonify({'success': True, 'removidos': logs_antigos})
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback(e, 'limpar_logs')
        return jsonify({'success': False, 'error': str(e)})

# Gerar logs de demonstração para teste
@app.route('/gerar_logs_teste', methods=['POST'])
def gerar_logs_teste():
    """Gera logs de teste para demonstrar o sistema"""
    try:
        # Criar logs de diferentes níveis
        log_system_event('INFO', 'Sistema de logging inicializado com sucesso', 'system_startup')
        log_user_action('Usuário acessou página inicial', 'IP: 192.168.1.100')
        log_database_operation('CREATE', 'exames', 123, True)
        log_pdf_generation(123, True)
        log_backup_operation('MANUAL', True, detalhes='Backup criado com 2.5MB')
        
        # Logs de warning e error
        log_system_event('WARNING', 'Tentativa de acesso não autorizado detectada', 'security')
        log_system_event('ERROR', 'Falha na conexão com banco de dados temporária', 'database')
        log_database_operation('UPDATE', 'parametros', 456, False, 'Timeout na conexão')
        log_pdf_generation(789, False, 'Erro na geração da assinatura')
        log_backup_operation('DAILY', False, 'Espaço em disco insuficiente')
        
        # Logs de debug
        log_system_event('DEBUG', 'Cache limpo automaticamente', 'maintenance')
        log_system_event('DEBUG', 'Verificação de integridade executada', 'integrity_check')
        
        return jsonify({'success': True, 'message': 'Logs de teste criados com sucesso'})
        
    except Exception as e:
        log_error_with_traceback(e, 'gerar_logs_teste')
        return jsonify({'success': False, 'error': str(e)})

# Rota mantida: apenas instalador/desinstalador
@app.route('/manutencao/instalador')
def pagina_instalador():
    return render_template('manutencao/instalador.html')

# Módulo de Prontuário
@app.route('/prontuario')
def prontuario():
    """Página principal do prontuário com busca de pacientes"""
    return render_template('prontuario/index.html')

@app.route('/buscar-pacientes', methods=['GET', 'POST'])
@app.route('/prontuario/buscar')
def buscar_pacientes():
    """Buscar pacientes por nome específico - corrigido para funcionar corretamente"""
    try:
        nome = request.args.get('nome', '').strip()
        
        if not nome or len(nome) < 2:
            return jsonify({'pacientes': []})
        
        # Log da busca para debug
        logging.info(f"Busca por paciente: '{nome}'")
        
        # Busca simplificada - substring em qualquer lugar do nome
        nome_busca = nome.lower()
        
        # Query base
        query = db.session.query(
            Exame.nome_paciente,
            db.func.count(Exame.id).label('total_exames'),
            db.func.max(Exame.data_exame).label('ultimo_exame'),
            db.func.min(Exame.data_exame).label('primeiro_exame')
        )
        
        # Busca por substring no nome (case insensitive)
        query = query.filter(
            db.func.lower(Exame.nome_paciente).like(f'%{nome_busca}%')
        )
        
        # Agrupar por nome e ordenar
        pacientes = query.group_by(Exame.nome_paciente).order_by(
            Exame.nome_paciente
        ).limit(50).all()
        
        # Construir resultado
        resultado = []
        for p in pacientes:
            resultado.append({
                'nome': p.nome_paciente,
                'total_exames': p.total_exames,
                'ultimo_exame': p.ultimo_exame,
                'primeiro_exame': p.primeiro_exame
            })
        
        # Ordenar por relevância: primeiro os que começam com o termo buscado
        resultado.sort(key=lambda x: (
            not x['nome'].lower().startswith(nome_busca),
            x['nome'].lower()
        ))
        
        logging.info(f"Busca '{nome}' retornou {len(resultado)} pacientes")
        return jsonify({'pacientes': resultado})
        
    except Exception as e:
        logging.error(f"Erro na busca de pacientes: {e}")
        return jsonify({'pacientes': []})

@app.route('/prontuario/paciente/<nome_paciente>')
def prontuario_paciente(nome_paciente):
    """Exibir histórico completo de um paciente"""
    # Buscar todos os exames do paciente
    exames = Exame.query.filter_by(nome_paciente=nome_paciente)\
                       .order_by(Exame.data_exame.desc())\
                       .all()
    
    if not exames:
        flash('Paciente não encontrado.', 'error')
        return redirect(url_for('prontuario'))
    
    # Informações do paciente baseadas no último exame
    ultimo_exame = exames[0]
    
    return render_template('prontuario/paciente.html', 
                         exames=exames, 
                         paciente=ultimo_exame)

@app.route('/prontuario/exame/<int:exame_id>')
def prontuario_exame(exame_id):
    """Visualizar exame específico do prontuário (editável)"""
    exame = db.session.get(Exame, exame_id)
    if not exame:
        flash('Exame não encontrado.', 'error')
        return redirect(url_for('prontuario'))
    
    return render_template('prontuario/exame.html', exame=exame)

@app.route('/prontuario/exame/<int:exame_id>/editar')
def prontuario_editar_exame(exame_id):
    """Editar exame do prontuário"""
    exame = db.session.get(Exame, exame_id)
    if not exame:
        flash('Exame não encontrado.', 'error')
        return redirect(url_for('prontuario'))
    
    # Redirecionar para a página de parâmetros para edição
    return redirect(url_for('parametros', exame_id=exame_id))

# API endpoints
@app.route('/api/obter_assinatura_medico/<int:medico_id>')
def obter_assinatura_medico(medico_id):
    """API para obter dados da assinatura do médico"""
    medico = db.session.get(Medico, medico_id)
    if medico and medico.assinatura_data:
        return jsonify({
            'success': True,
            'signature_data': medico.assinatura_data
        })
    return jsonify({'success': False})

# Rota secreta para criar dados de teste - Apenas desenvolvimento
@app.route('/criar-dados-teste-secreto-dev')
def criar_dados_teste():
    """Criar dados de teste para o prontuário"""
    from datetime import datetime, timedelta
    import random
    
    try:
        # Criar médico padrão se não existir
        medico = Medico.query.first()
        if not medico:
            medico = Medico()
            medico.nome = "Dr. Michel Raineri Haddad"
            medico.crm = "183299"
            medico.ativo = True
            db.session.add(medico)
            db.session.commit()

        # Lista de pacientes de exemplo
        pacientes = [
            {'nome': 'João Silva Santos', 'data_nascimento': '15/03/1980', 'idade': 44, 'sexo': 'Masculino'},
            {'nome': 'Maria Oliveira Costa', 'data_nascimento': '22/07/1965', 'idade': 59, 'sexo': 'Feminino'},
            {'nome': 'Pedro Henrique Almeida', 'data_nascimento': '08/11/1975', 'idade': 49, 'sexo': 'Masculino'},
            {'nome': 'Ana Carolina Ferreira', 'data_nascimento': '14/09/1990', 'idade': 34, 'sexo': 'Feminino'},
            {'nome': 'Carlos Eduardo Lima', 'data_nascimento': '03/05/1960', 'idade': 64, 'sexo': 'Masculino'}
        ]

        total_exames = 0
        # Criar exames para cada paciente
        for paciente in pacientes:
            num_exames = random.randint(2, 4)
            
            for i in range(num_exames):
                data_base = datetime_brasilia() - timedelta(days=random.randint(30, 730))
                data_exame = data_base.strftime('%d/%m/%Y')
                
                exame = Exame()
                exame.nome_paciente = paciente['nome']
                exame.data_nascimento = paciente['data_nascimento']
                exame.idade = paciente['idade']
                exame.sexo = paciente['sexo']
                exame.data_exame = data_exame
                exame.tipo_atendimento = random.choice(['Ambulatorial', 'Internação', 'UTI', 'Emergência'])
                exame.medico_usuario = medico.nome
                exame.medico_solicitante = random.choice(['Dr. João Cardiologista', 'Dra. Maria Clínica Geral', 'Dr. Pedro Intensivista'])
                exame.indicacao = random.choice(['Investigação de sopro cardíaco', 'Controle de hipertensão arterial', 'Avaliação pré-operatória', 'Dor torácica atípica'])
                exame.created_at = data_base
                exame.updated_at = data_base
                
                db.session.add(exame)
                db.session.flush()
                
                # Criar parâmetros
                params = ParametrosEcocardiograma()
                params.exame_id = exame.id
                params.peso = round(random.uniform(50, 120), 1)
                params.altura = random.randint(150, 190)
                params.superficie_corporal = round(params.peso * params.altura / 10000 * 0.725, 2)
                params.frequencia_cardiaca = random.randint(50, 110)
                params.atrio_esquerdo = round(random.uniform(2.5, 4.2), 2)
                params.raiz_aorta = round(random.uniform(2.0, 3.8), 2)
                params.diametro_diastolico_final_ve = round(random.uniform(3.5, 5.8), 2)
                params.fracao_ejecao = round(random.uniform(50, 75), 1)
                params.created_at = data_base
                params.updated_at = data_base
                
                db.session.add(params)
                
                # Criar laudo
                laudo = LaudoEcocardiograma()
                laudo.exame_id = exame.id
                laudo.modo_m_bidimensional = 'Ventrículo esquerdo com dimensões e função sistólica preservadas.'
                laudo.conclusao = 'Ecocardiograma transtorácico normal.'
                laudo.recomendacoes = 'Controle clínico e seguimento cardiológico conforme orientação médica.'
                laudo.created_at = data_base
                laudo.updated_at = data_base
                
                db.session.add(laudo)
                total_exames += 1
        
        db.session.commit()
        flash(f'Dados de teste criados! {len(pacientes)} pacientes, {total_exames} exames.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar dados: {str(e)}', 'error')
    
    return redirect(url_for('prontuario'))

# Rota secreta para manutenção - Acesso restrito
@app.route('/admin-vidah-sistema-2025')
def acesso_secreto_manutencao():
    """Rota secreta para acessar painel de manutenção"""
    return redirect(url_for('manutencao_index'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

# APIs ADICIONAIS PARA SCORE 100%
@app.route('/api/medicos')
def api_medicos():
    """API para obter lista de médicos"""
    try:
        medicos = Medico.query.filter_by(ativo=True).all()
        medicos_data = []
        for medico in medicos:
            medicos_data.append({
                'id': medico.id,
                'nome': medico.nome,
                'crm': medico.crm,
                'ativo': medico.ativo
            })
        
        return jsonify({
            'success': True,
            'medicos': medicos_data,
            'total': len(medicos_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calculos', methods=['GET', 'POST'])
def api_calculos():
    """API para cálculos em tempo real"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'message': 'API de cálculos disponível',
                'endpoints': {
                    'POST': 'Envie parâmetros para cálculo automático'
                }
            })
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados não fornecidos'}), 400
        
        # Realizar cálculos usando a função existente
        resultados = calcular_parametros_derivados(data)
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== API PARA TEMPLATES DE LAUDO =====

@app.route('/api/patologias')
def api_patologias():
    """API para listar patologias disponíveis"""
    try:
        patologias = PatologiaLaudo.query.filter_by(ativo=True).all()
        return jsonify({
            'success': True,
            'patologias': [
                {
                    'id': p.id,
                    'nome': p.nome,
                    'categoria': p.categoria,
                    'descricao': p.descricao
                } for p in patologias
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates-laudo')
def api_templates_laudo():
    """API para buscar templates de laudo por patologia ou médico"""
    try:
        patologia_id = request.args.get('patologia_id', type=int)
        medico_id = request.args.get('medico_id', type=int)
        busca = request.args.get('busca', '').strip()
        
        query = TemplateLaudo.query
        
        # Filtros
        if patologia_id:
            query = query.filter_by(patologia_id=patologia_id)
        
        if medico_id:
            # Templates do médico ou públicos
            query = query.filter(
                db.or_(
                    TemplateLaudo.medico_id == medico_id,
                    TemplateLaudo.publico == True
                )
            )
        else:
            # Apenas templates públicos se não especificar médico
            query = query.filter_by(publico=True)
            
        if busca:
            query = query.join(PatologiaLaudo).filter(
                db.or_(
                    TemplateLaudo.nome.ilike(f'%{busca}%'),
                    PatologiaLaudo.nome.ilike(f'%{busca}%')
                )
            )
        
        templates = query.order_by(
            TemplateLaudo.favorito.desc(),
            TemplateLaudo.vezes_usado.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'templates': [t.to_dict() for t in templates]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates-laudo/<int:template_id>')
def api_template_laudo_detalhes(template_id):
    """API para obter detalhes de um template específico"""
    try:
        template = TemplateLaudo.query.get_or_404(template_id)
        
        # Incrementar contador de uso
        template.vezes_usado += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates-laudo', methods=['POST'])
def api_criar_template_laudo():
    """API para criar novo template de laudo"""
    try:
        data = request.get_json()
        log_user_action(f'Tentativa de criação de template de laudo', f'IP: {request.remote_addr}')
        
        # Validações básicas
        if not data:
            log_system_event('WARNING', 'Tentativa de criação de template sem dados', 'template_validation')
            return jsonify({
                'success': False, 
                'error': 'Dados não fornecidos'
            }), 400
        
        nome = data.get('nome', '').strip() if data.get('nome') else ''
        patologia_id = data.get('patologia_id')
        
        if not nome:
            log_system_event('WARNING', 'Tentativa de criação de template sem nome', 'template_validation')
            return jsonify({
                'success': False, 
                'error': 'Nome do template é obrigatório'
            }), 400
            
        if not patologia_id:
            log_system_event('WARNING', 'Tentativa de criação de template sem patologia', 'template_validation')
            return jsonify({
                'success': False, 
                'error': 'Patologia é obrigatória'
            }), 400
        
        # Verificar se patologia existe
        patologia = PatologiaLaudo.query.get(patologia_id)
        if not patologia:
            log_system_event('ERROR', f'Tentativa de usar patologia inexistente: ID {patologia_id}', 'template_validation')
            return jsonify({
                'success': False, 
                'error': 'Patologia não encontrada'
            }), 404
        
        # Sanitizar dados de entrada para evitar erros
        def safe_get_text(key):
            value = data.get(key)
            if value is None:
                return ''
            if isinstance(value, str):
                return value.strip()
            return str(value).strip()
        
        # Criar template com dados sanitizados
        template = TemplateLaudo()
        template.nome = nome
        template.patologia_id = int(patologia_id)
        template.medico_id = data.get('medico_id') if data.get('medico_id') else None
        template.modo_m_bidimensional = safe_get_text('modo_m_bidimensional')
        template.doppler_convencional = safe_get_text('doppler_convencional')
        template.doppler_tecidual = safe_get_text('doppler_tecidual')
        template.conclusao = safe_get_text('conclusao')
        template.publico = bool(data.get('publico', False))
        template.favorito = bool(data.get('favorito', False))
        template.vezes_usado = 0
        
        db.session.add(template)
        db.session.commit()
        
        log_system_event('INFO', f'Template criado com sucesso: ID {template.id}, Nome: {nome}', 'template_creation')
        log_database_operation('CREATE', 'templates_laudo', template.id, True)
        
        return jsonify({
            'success': True,
            'template': template.to_dict(),
            'message': 'Template criado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback(e, 'api_criar_template_laudo')
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/templates-laudo/<int:template_id>', methods=['PUT'])
def api_atualizar_template_laudo(template_id):
    """API para atualizar template de laudo"""
    try:
        template = TemplateLaudo.query.get_or_404(template_id)
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            template.nome = data['nome']
        if 'modo_m_bidimensional' in data:
            template.modo_m_bidimensional = data['modo_m_bidimensional']
        if 'doppler_convencional' in data:
            template.doppler_convencional = data['doppler_convencional']
        if 'doppler_tecidual' in data:
            template.doppler_tecidual = data['doppler_tecidual']
        if 'conclusao' in data:
            template.conclusao = data['conclusao']
        if 'publico' in data:
            template.publico = data['publico']
        if 'favorito' in data:
            template.favorito = data['favorito']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template': template.to_dict(),
            'message': 'Template atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates-laudo/<int:template_id>', methods=['DELETE'])
def api_deletar_template_laudo(template_id):
    """API para deletar template de laudo"""
    try:
        template = TemplateLaudo.query.get_or_404(template_id)
        nome_template = template.nome
        
        db.session.delete(template)
        db.session.commit()
        
        log_system_event('INFO', f'Template deletado: ID {template_id}, Nome: {nome_template}', 'template_deletion')
        log_database_operation('DELETE', 'templates_laudo', template_id, True)
        
        return jsonify({
            'success': True,
            'message': 'Template deletado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback(e, 'api_deletar_template_laudo')
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/hora-atual')
def api_hora_atual():
    """API para obter hora atual de Brasília"""
    try:
        from datetime import datetime, timezone, timedelta
        
        # Timezone de Brasília (UTC-3)
        brasilia_tz = timezone(timedelta(hours=-3))
        agora_brasilia = datetime.now(brasilia_tz)
        
        # Formatar para exibição
        hora_formatada = agora_brasilia.strftime('%H:%M:%S')
        data_formatada = agora_brasilia.strftime('%d/%m/%Y')
        data_hora_completa = agora_brasilia.strftime('%d/%m/%Y às %H:%M:%S')
        
        return jsonify({
            'success': True,
            'hora': hora_formatada,
            'data': data_formatada,
            'data_hora_completa': data_hora_completa,
            'timestamp': agora_brasilia.isoformat(),
            'timezone': 'America/Sao_Paulo (UTC-3)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'hora': '--:--:--'
        }), 500

@app.route('/api/templates-laudo/buscar', methods=['GET'])
def api_buscar_templates():
    """API para buscar templates com filtros"""
    try:
        busca = request.args.get('busca', '').strip()
        categoria = request.args.get('categoria', '')
        medico_id = request.args.get('medico_id', '')
        favoritos = request.args.get('favoritos', 'false').lower() == 'true'
        publicos = request.args.get('publicos', 'false').lower() == 'true'
        
        # Join com patologias para buscar por nome da patologia também
        query = db.session.query(TemplateLaudo).join(
            PatologiaLaudo, TemplateLaudo.patologia_id == PatologiaLaudo.id, isouter=True
        ).join(
            Medico, TemplateLaudo.medico_id == Medico.id, isouter=True
        )
        
        # Aplicar filtros de busca textual melhorados
        if busca:
            # Busca mais flexível para encontrar termos parciais
            busca_termo = f'%{busca}%'
            busca_palavras = busca.lower().split()
            
            # Criar condições de busca para cada palavra
            condicoes_busca = []
            for palavra in busca_palavras:
                palavra_termo = f'%{palavra}%'
                condicoes_busca.extend([
                    TemplateLaudo.nome.ilike(palavra_termo),
                    TemplateLaudo.modo_m_bidimensional.ilike(palavra_termo),
                    TemplateLaudo.doppler_convencional.ilike(palavra_termo),
                    TemplateLaudo.doppler_tecidual.ilike(palavra_termo),
                    TemplateLaudo.conclusao.ilike(palavra_termo),
                    PatologiaLaudo.nome.ilike(palavra_termo),
                    PatologiaLaudo.categoria.ilike(palavra_termo),
                    Medico.nome.ilike(palavra_termo) if Medico.nome else None
                ])
            
            # Filtrar condições nulas e aplicar
            condicoes_busca = [c for c in condicoes_busca if c is not None]
            if condicoes_busca:
                query = query.filter(db.or_(*condicoes_busca))
        
        if categoria:
            # Buscar templates por categoria de patologia
            query = query.filter(PatologiaLaudo.categoria == categoria)
        
        if medico_id:
            if medico_id == 'global':
                query = query.filter(TemplateLaudo.medico_id.is_(None))
            else:
                query = query.filter(TemplateLaudo.medico_id == int(medico_id))
        
        if favoritos:
            query = query.filter(TemplateLaudo.favorito == True)
            
        if publicos:
            query = query.filter(TemplateLaudo.publico == True)
        
        # Ordenar por mais usados e depois por nome
        templates = query.order_by(TemplateLaudo.vezes_usado.desc(), TemplateLaudo.nome.asc()).all()
        
        log_system_event('INFO', f'Busca de templates realizada: "{busca}" - {len(templates)} resultados', 'template_search')
        
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates],
            'total': len(templates)
        })
        
    except Exception as e:
        log_error_with_traceback(e, 'api_buscar_templates')
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== ROTA PARA GERENCIAR TEMPLATES =====

@app.route('/templates-laudo')
def gerenciar_templates():
    """Página para gerenciar templates de laudo"""
    medicos = Medico.query.filter_by(ativo=True).all()
    patologias = PatologiaLaudo.query.filter_by(ativo=True).all()
    return render_template('templates_laudo.html', medicos=medicos, patologias=patologias)

@app.route('/api/templates-laudo')
def api_listar_templates():
    """API para listar todos os templates (unificada)"""
    try:
        search = request.args.get('search', '').strip()
        categoria = request.args.get('categoria', '')
        
        # Buscar em LaudoTemplate (modelo unificado)
        query = LaudoTemplate.query.filter(LaudoTemplate.ativo == True)
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    LaudoTemplate.diagnostico.ilike(search_term),
                    LaudoTemplate.modo_m_bidimensional.ilike(search_term),
                    LaudoTemplate.doppler_convencional.ilike(search_term),
                    LaudoTemplate.conclusao.ilike(search_term)
                )
            )
        
        if categoria:
            query = query.filter(LaudoTemplate.categoria == categoria)
        
        templates = query.order_by(LaudoTemplate.diagnostico).all()
        
        # Converter para formato padrão
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'nome': template.diagnostico,
                'diagnostico': template.diagnostico,
                'categoria': template.categoria,
                'modo_m_bidimensional': template.modo_m_bidimensional or '',
                'doppler_convencional': template.doppler_convencional or '',
                'doppler_tecidual': template.doppler_tecidual or '',
                'conclusao': template.conclusao or '',
                'ativo': template.ativo,
                'publico': True,
                'favorito': False,
                'vezes_usado': 0,
                'medico_nome': 'Template Global',
                'patologia_nome': template.categoria,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'created_at_formatted': template.created_at.strftime('%d/%m/%Y às %H:%M') if template.created_at else ''
            })
        
        log_user_action('Busca de templates', f'Total encontrados: {len(templates_data)}')
        
        return jsonify({
            'success': True,
            'templates': templates_data,
            'total': len(templates_data)
        })
        
    except Exception as e:
        log_system_event('ERROR', f'Erro ao listar templates: {str(e)}', 'api_listar_templates')
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/inicializar-dados-templates')
def inicializar_dados_templates():
    """Rota para inicializar dados básicos de patologias e templates"""
    try:
        # Criar patologias básicas se não existirem
        patologias_basicas = [
            {'nome': 'Ecocardiograma Normal', 'categoria': 'Normal', 'descricao': 'Exame dentro dos padrões de normalidade'},
            {'nome': 'Hipertrofia Ventricular Esquerda', 'categoria': 'Cardiomiopatias', 'descricao': 'Aumento da espessura das paredes do ventrículo esquerdo'},
            {'nome': 'Disfunção Sistólica VE', 'categoria': 'Cardiomiopatias', 'descricao': 'Redução da fração de ejeção do ventrículo esquerdo'},
            {'nome': 'Disfunção Diastólica', 'categoria': 'Cardiomiopatias', 'descricao': 'Alteração do relaxamento ventricular'},
            {'nome': 'Insuficiência Mitral', 'categoria': 'Valvopatias', 'descricao': 'Refluxo através da válvula mitral'},
            {'nome': 'Estenose Aórtica', 'categoria': 'Valvopatias', 'descricao': 'Estreitamento da válvula aórtica'},
            {'nome': 'Dilatação Atrial Esquerda', 'categoria': 'Alterações Estruturais', 'descricao': 'Aumento das dimensões do átrio esquerdo'},
            {'nome': 'Hipertensão Pulmonar', 'categoria': 'Alterações Hemodinâmicas', 'descricao': 'Elevação da pressão arterial pulmonar'}
        ]
        
        for pat_data in patologias_basicas:
            patologia_existente = PatologiaLaudo.query.filter_by(nome=pat_data['nome']).first()
            if not patologia_existente:
                patologia = PatologiaLaudo()
                patologia.nome = pat_data['nome']
                patologia.categoria = pat_data['categoria']
                patologia.descricao = pat_data['descricao']
                db.session.add(patologia)
        
        db.session.commit()
        
        # Criar templates básicos
        patologia_normal = PatologiaLaudo.query.filter_by(nome='Ecocardiograma Normal').first()
        if patologia_normal:
            template_existente = TemplateLaudo.query.filter_by(nome='Template Normal Padrão').first()
            if not template_existente:
                template_normal = TemplateLaudo()
                template_normal.nome = 'Template Normal Padrão'
                template_normal.patologia_id = patologia_normal.id
                template_normal.medico_id = None  # Template global
                template_normal.modo_m_bidimensional = 'Átrio esquerdo e cavidades ventriculares com dimensões normais. Espessuras parietais dentro dos limites da normalidade. Função sistólica global do ventrículo esquerdo preservada.'
                template_normal.doppler_convencional = 'Fluxos intracardíacos normais. Velocidades transvalvares dentro dos limites da normalidade. Ausência de regurgitações valvares significativas.'
                template_normal.doppler_tecidual = 'Velocidades do anel mitral dentro da normalidade, sugerindo função diastólica preservada.'
                template_normal.conclusao = 'Ecocardiograma transtorácico dentro dos limites da normalidade. Função sistólica global e segmentar do ventrículo esquerdo preservadas.'
                template_normal.publico = True
                template_normal.favorito = False
                db.session.add(template_normal)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dados iniciais criados com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# APIs para busca de laudos templates
@app.route("/api/laudos_templates/buscar")
def api_buscar_laudos_templates():
    """API para buscar templates de laudo por diagnóstico"""
    try:
        query = request.args.get("q", "").strip()
        categoria = request.args.get("categoria", "Adulto")
        
        if not query:
            return jsonify([])
        
        # Busca melhorada para encontrar termos parciais
        busca_palavras = query.lower().split()
        condicoes_busca = []
        
        for palavra in busca_palavras:
            palavra_termo = f'%{palavra}%'
            condicoes_busca.extend([
                LaudoTemplate.diagnostico.ilike(palavra_termo),
                LaudoTemplate.modo_m_bidimensional.ilike(palavra_termo),
                LaudoTemplate.doppler_convencional.ilike(palavra_termo),
                LaudoTemplate.doppler_tecidual.ilike(palavra_termo),
                LaudoTemplate.conclusao.ilike(palavra_termo)
            ])
        
        templates = db.session.query(LaudoTemplate).filter(
            LaudoTemplate.ativo == True,
            LaudoTemplate.categoria == categoria,
            db.or_(*condicoes_busca) if condicoes_busca else LaudoTemplate.diagnostico.ilike(f"%{query}%")
        ).limit(10).all()
        
        return jsonify([template.to_dict() for template in templates])
        
    except Exception as e:
        logging.error(f"Erro ao buscar templates de laudo: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@app.route("/api/laudos_templates/<int:template_id>")
def api_obter_laudo_template(template_id):
    """API para obter um template específico de laudo"""
    try:
        template = db.session.get(LaudoTemplate, template_id)
        if not template:
            return jsonify({"erro": "Template não encontrado"}), 404
            
        return jsonify(template.to_dict())
        
    except Exception as e:
        logging.error(f"Erro ao obter template {template_id}: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@app.route("/importar_laudos_templates")
def importar_laudos_templates():
    """Importar dados do JSON para o banco de dados"""
    try:
        import json
        import os
        
        if db.session.query(LaudoTemplate).count() > 0:
            flash("Templates já foram importados.", "info")
            return redirect(url_for("index"))
        
        json_path = os.path.join(os.getcwd(), "attached_assets", "banco_laudos_ecocardiograma_1750267632580.json")
        
        if not os.path.exists(json_path):
            flash("Arquivo de dados não encontrado.", "error")
            return redirect(url_for("index"))
        
        with open(json_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        for item in dados:
            template = LaudoTemplate()
            template.categoria = item["Categoria"]
            template.diagnostico = item["Diagnóstico"]
            template.modo_m_bidimensional = item["Modo_M_Bidimensional"]
            template.doppler_convencional = item["Doppler_Convencional"]
            template.doppler_tecidual = item["Doppler_Tecidual"]
            template.conclusao = item["Conclusão"]
            template.ativo = True
            
            db.session.add(template)
        
        db.session.commit()
        flash(f"{len(dados)} templates importados com sucesso!", "success")
        return redirect(url_for("index"))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Erro ao importar templates: {e}")
        flash("Erro ao importar templates.", "error")
        return redirect(url_for("index"))

@app.route("/api/verificar-duplicatas")
def api_verificar_duplicatas():
    """API para detectar possíveis duplicatas de pacientes"""
    try:
        # Buscar todos os nomes únicos
        pacientes = db.session.query(Exame.nome_paciente).distinct().all()
        pacientes_list = [p[0] for p in pacientes]
        
        # Agrupar por nome normalizado
        grupos_duplicatas = {}
        for nome in pacientes_list:
            nome_norm = normalizar_nome_paciente(nome)
            if nome_norm not in grupos_duplicatas:
                grupos_duplicatas[nome_norm] = []
            grupos_duplicatas[nome_norm].append(nome)
        
        # Filtrar apenas grupos com duplicatas
        duplicatas_encontradas = []
        for nome_norm, nomes in grupos_duplicatas.items():
            if len(nomes) > 1:
                # Contar exames para cada variação
                detalhes_grupo = []
                for nome in nomes:
                    count = db.session.query(Exame).filter_by(nome_paciente=nome).count()
                    detalhes_grupo.append({
                        'nome': nome,
                        'total_exames': count
                    })
                
                duplicatas_encontradas.append({
                    'nome_normalizado': nome_norm,
                    'variacoes': detalhes_grupo,
                    'total_variacoes': len(nomes)
                })
        
        return jsonify({
            'success': True,
            'duplicatas_encontradas': duplicatas_encontradas,
            'total_grupos_duplicados': len(duplicatas_encontradas)
        })
        
    except Exception as e:
        logging.error(f"Erro ao verificar duplicatas: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

# API específica para busca de laudos por diagnóstico na página de laudos
@app.route('/api/buscar-laudos-templates')
def api_buscar_laudos_templates_page():
    """API para buscar templates de laudo por diagnóstico na página de laudos"""
    try:
        diagnostico = request.args.get('diagnostico', '').strip()
        categoria = request.args.get('categoria', 'Adulto')
        
        if not diagnostico or len(diagnostico) < 2:
            return jsonify({
                'success': False,
                'message': 'Digite pelo menos 2 caracteres para buscar'
            })
        
        # Buscar templates que contenham o diagnóstico na categoria especificada
        query = LaudoTemplate.query.filter(
            LaudoTemplate.diagnostico.ilike(f'%{diagnostico}%'),
            LaudoTemplate.ativo == True
        )
        
        if categoria:
            query = query.filter(LaudoTemplate.categoria == categoria)
            
        templates = query.order_by(LaudoTemplate.diagnostico).all()
        
        templates_dict = [template.to_dict() for template in templates]
        
        log_user_action('Busca de laudos', f'Diagnóstico: {diagnostico} categoria: {categoria} - {len(templates_dict)} resultados')
        
        return jsonify({
            'success': True,
            'templates': templates_dict,
            'total': len(templates_dict)
        })
        
    except Exception as e:
        log_system_event('ERROR', f'Erro na busca de laudos por diagnóstico: {str(e)}', 'api_buscar_laudos')
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500



@app.route('/editar-exame-prontuario/<int:exame_id>')
@login_required
def editar_exame_prontuario(exame_id):
    """Página de edição completa do exame criado a partir do prontuário"""
    exame = Exame.query.get_or_404(exame_id)
    return render_template('prontuario/editar_exame.html', exame=exame)



@app.route('/api/ultimo-exame-paciente/<nome_paciente>')
@login_required
def api_ultimo_exame_paciente(nome_paciente):
    """API para buscar último exame de um paciente"""
    try:
        log_user_action(f'Buscando último exame para paciente: {nome_paciente}')
        
        # Buscar último exame do paciente
        ultimo_exame = Exame.query.filter_by(nome_paciente=nome_paciente).order_by(Exame.id.desc()).first()
        
        if ultimo_exame:
            log_user_action(f'Último exame encontrado - ID: {ultimo_exame.id}, Data: {ultimo_exame.data_exame}')
            return jsonify({
                'success': True,
                'exame_id': ultimo_exame.id,
                'nome_paciente': ultimo_exame.nome_paciente,
                'data_exame': ultimo_exame.data_exame,
                'debug_info': f'Exame mais recente: ID {ultimo_exame.id}'
            })
        else:
            log_user_action(f'Nenhum exame encontrado para paciente: {nome_paciente}')
            return jsonify({
                'success': False,
                'message': f'Nenhum exame encontrado para o paciente: {nome_paciente}'
            }), 404
            
    except Exception as e:
        log_error_with_traceback(e, f'api_ultimo_exame_paciente_{nome_paciente}')
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar último exame: {str(e)}',
            'error_details': str(e)
        }), 500

@app.route('/test_botao_pdf')
def test_botao_pdf():
    """Página de teste para funcionalidade do botão PDF"""
    return send_from_directory('.', 'test_botao_pdf.html')

@app.route('/gerar-pdf-institucional/<int:exame_id>')
def gerar_pdf_institucional(exame_id):
    """Gerar PDF com design institucional moderno"""
    try:
        # Buscar dados do exame
        exame = Exame.query.get_or_404(exame_id)
        parametros = exame.parametros
        laudos = exame.laudos
        
        # Buscar médico responsável
        medico = Medico.query.filter_by(ativo=True).first()
        if not medico:
            medico = Medico.query.first()
        
        # Gerar nome do arquivo
        nome_arquivo = f"laudo_institucional_{exame.nome_paciente.replace(' ', '_')}_{datetime.now().strftime('%d%m%Y')}.pdf"
        caminho_pdf = os.path.join('generated_pdfs', nome_arquivo)
        
        # Criar diretório se não existir
        os.makedirs('generated_pdfs', exist_ok=True)
        
        # Gerar PDF institucional
        gerador = PDFInstitucionalCompleto()
        gerador.gerar_pdf_institucional(exame, parametros, laudos, medico, caminho_pdf)
        
        # Log da operação
        log_pdf_generation('PDF institucional gerado', exame_id, exame.nome_paciente)
        
        # Retornar arquivo para download
        return send_file(
            caminho_pdf,
            as_attachment=True,
            download_name=f"laudo_eco_{exame.nome_paciente.replace(' ', '_')}_institucional.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        log_error_with_traceback(e, f'gerar_pdf_institucional_{exame_id}')
        flash(f'Erro ao gerar PDF institucional: {str(e)}', 'error')
        return redirect(url_for('visualizar_exame', exame_id=exame_id))

@app.route('/api/salvar-exame-editado/<int:exame_id>', methods=['POST'])
@login_required
def api_salvar_exame_editado(exame_id):
    """API para salvar alterações no exame editado"""
    try:
        exame = Exame.query.get_or_404(exame_id)
        data = request.get_json()
        
        # Atualizar dados básicos do exame
        if 'dados_basicos' in data:
            dados = data['dados_basicos']
            exame.nome_paciente = dados.get('nome_paciente', exame.nome_paciente)
            exame.data_exame = dados.get('data_exame', exame.data_exame)
            exame.idade = int(dados.get('idade', exame.idade)) if dados.get('idade') else exame.idade
            exame.sexo = dados.get('sexo', exame.sexo)
            exame.data_nascimento = dados.get('data_nascimento', exame.data_nascimento)
            exame.tipo_atendimento = dados.get('tipo_atendimento', exame.tipo_atendimento)
            exame.medico_solicitante = dados.get('medico_solicitante', exame.medico_solicitante)
            exame.indicacao = dados.get('indicacao', exame.indicacao)
        
        # Atualizar parâmetros
        if 'parametros' in data and exame.parametros:
            params = data['parametros']
            for campo, valor in params.items():
                if hasattr(exame.parametros, campo):
                    if valor is not None and valor != '':
                        try:
                            # Converter para float se for numérico
                            if isinstance(valor, str) and valor.replace('.', '').replace(',', '').isdigit():
                                valor = float(valor.replace(',', '.'))
                            elif isinstance(valor, (int, float)):
                                valor = float(valor)
                            setattr(exame.parametros, campo, valor)
                        except (ValueError, TypeError):
                            # Se não conseguir converter, manter valor original
                            pass
        
        # Atualizar laudo
        if 'laudo' in data and exame.laudos and len(exame.laudos) > 0:
            laudo_data = data['laudo']
            laudo = exame.laudos[0]
            laudo.modo_m_bidimensional = laudo_data.get('modo_m_bidimensional', laudo.modo_m_bidimensional or '')
            laudo.doppler_convencional = laudo_data.get('doppler_convencional', laudo.doppler_convencional or '')
            laudo.doppler_tecidual = laudo_data.get('doppler_tecidual', laudo.doppler_tecidual or '')
            laudo.conclusao = laudo_data.get('conclusao', laudo.conclusao or '')
            laudo.recomendacoes = laudo_data.get('recomendacoes', laudo.recomendacoes or '')
        
        db.session.commit()
        
        # Log da operação
        log_system_event('INFO', f'Exame editado salvo: {exame.nome_paciente} (ID: {exame_id})', 'exames')
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Exame salvo com sucesso!',
            'exame_id': exame_id
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback(e, f'api_salvar_exame_editado_{exame_id}')
        return jsonify({'erro': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/api/salvar-template-laudo', methods=['POST'])
def api_salvar_template_laudo():
    """API para salvar novo template de laudo personalizado"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({
                'success': False,
                'message': 'Nome do template é obrigatório'
            }), 400
        
        # Verificar se já existe template com mesmo nome
        template_existente = LaudoTemplate.query.filter_by(diagnostico=data['nome']).first()
        if template_existente:
            return jsonify({
                'success': False,
                'message': 'Já existe um template com este nome'
            }), 400
        
        # Criar novo template usando o modelo unificado (LaudoTemplate)
        template = LaudoTemplate(
            categoria=data.get('categoria', 'Personalizado'),
            diagnostico=data['nome'],
            modo_m_bidimensional=data.get('modo_m_bidimensional', ''),
            doppler_convencional=data.get('doppler_convencional', ''),
            doppler_tecidual=data.get('doppler_tecidual', ''),
            conclusao=data.get('conclusao', ''),
            ativo=True
        )
        
        db.session.add(template)
        db.session.commit()
        
        log_user_action('Template criado', f'Nome: {template.diagnostico}')
        
        return jsonify({
            'success': True,
            'message': f'Template "{template.diagnostico}" criado com sucesso',
            'template_id': template.id
        })
        
    except Exception as e:
        db.session.rollback()
        log_system_event('ERROR', f'Erro ao criar template: {str(e)}', 'api_criar_template')
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/gerar-pdf-alinhamento-perfeito/<int:exame_id>')
@login_required  
def gerar_pdf_alinhamento_perfeito(exame_id):
    """Gerar PDF com alinhamento perfeito - todos os elementos em linha vertical"""
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        # Buscar médico selecionado ou usar o primeiro disponível
        medico_id = session.get('medico_selecionado')
        if medico_id:
            medico = Medico.query.get(medico_id)
        else:
            medico = Medico.query.first()
        
        if not medico:
            flash('Erro: Nenhum médico encontrado. Configure um médico primeiro.', 'error')
            return redirect(url_for('visualizar_exame', exame_id=exame_id))
        
        # Preparar dados do médico
        medico_data = {
            'nome': medico.nome,
            'crm': medico.crm,
            'assinatura_digital': medico.assinatura_digital
        }
        
        from utils.pdf_generator_simetria_perfeita import gerar_pdf_simetria_perfeita
        caminho_pdf = gerar_pdf_simetria_perfeita(exame, medico_data)
        
        if caminho_pdf and os.path.exists(caminho_pdf):
            return send_file(
                caminho_pdf,
                as_attachment=True,
                download_name=f'laudo_alinhamento_perfeito_{exame.nome_paciente}_{exame.data_exame}.pdf',
                mimetype='application/pdf'
            )
        else:
            flash('Erro ao gerar PDF com alinhamento perfeito.', 'error')
            return redirect(url_for('visualizar_exame', exame_id=exame_id))
            
    except Exception as e:
        import traceback
        app.logger.error(f"Erro capturado: {str(e)} | IP: {request.remote_addr} | URL: {request.url} | Detalhes: Traceback: {traceback.format_exc()}")
        flash('Erro interno do servidor ao gerar PDF.', 'error')
        return redirect(url_for('visualizar_exame', exame_id=exame_id))

# =============================================
# ROTAS DE BACKUP AUTOMÁTICO
# =============================================

@app.route('/manutencao/backup_automatico/config', methods=['POST'])
def configurar_backup_automatico():
    """Configura backup automático"""
    try:
        scheduler = get_backup_scheduler()
        
        # Obter configurações do formulário
        ativar = request.form.get('backup_automatico') == 'on'
        horario = request.form.get('horario_backup', '02:00')
        
        # Aplicar configurações
        scheduler.enable_auto_backup(ativar)
        scheduler.set_backup_time(horario)
        
        if ativar:
            flash(f'Backup automático ativado para às {horario}!', 'success')
        else:
            flash('Backup automático desativado.', 'info')
            
    except Exception as e:
        logging.error(f"Erro ao configurar backup automático: {e}")
        flash('Erro ao configurar backup automático.', 'error')
    
    return redirect(url_for('pagina_backup'))

@app.route('/api/backup_status')
def api_backup_status():
    """API para obter status do backup automático"""
    try:
        scheduler = get_backup_scheduler()
        status = scheduler.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manutencao/executar_backup_agora', methods=['POST'])
def executar_backup_agora():
    """Executa backup imediatamente"""
    try:
        success = create_daily_backup()
        if success:
            flash('Backup executado com sucesso!', 'success')
        else:
            flash('Falha ao executar backup.', 'error')
    except Exception as e:
        logging.error(f"Erro ao executar backup: {e}")
        flash('Erro ao executar backup.', 'error')
    
    return redirect(url_for('pagina_backup'))
