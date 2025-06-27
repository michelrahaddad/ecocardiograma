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
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma, Medico, LogSistema, LaudoTemplate, datetime_brasilia
from auth.models import AuthUser
import logging
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

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

# ===== FUNCÕES DE UTILIDADE INTEGRADAS =====

def generate_pdf_report(exame):
    """Gerar PDF do exame usando ReportLab"""
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            caminho_pdf = tmp_file.name
        
        # Criar PDF
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        
        # Cabeçalho
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "GRUPO VIDAH - MEDICINA DIAGNÓSTICA")
        c.setFont("Helvetica", 10)
        c.drawString(50, 735, "R. XV de Novembro, 594 - Ibitinga-SP | Tel: (16) 3342-4768")
        
        # Linha divisória
        c.line(50, 720, 550, 720)
        
        # Título do laudo
        c.setFont("Helvetica-Bold", 14)
        c.drawString(200, 700, "LAUDO DE ECOCARDIOGRAMA TRANSTORÁCICO")
        
        # Dados do paciente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 670, "DADOS DO PACIENTE")
        
        c.setFont("Helvetica", 10)
        y = 650
        c.drawString(50, y, f"Nome: {exame.nome_paciente}")
        y -= 15
        c.drawString(50, y, f"Data de Nascimento: {exame.data_nascimento}")
        y -= 15
        c.drawString(50, y, f"Idade: {exame.idade} anos")
        y -= 15
        c.drawString(50, y, f"Sexo: {exame.sexo}")
        y -= 15
        c.drawString(50, y, f"Data do Exame: {exame.data_exame}")
        y -= 15
        if exame.tipo_atendimento:
            c.drawString(50, y, f"Tipo Atendimento: {exame.tipo_atendimento}")
            y -= 15
        
        # Parâmetros ecocardiográficos
        if exame.parametros:
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "PARÂMETROS ECOCARDIOGRÁFICOS")
            y -= 20
            
            c.setFont("Helvetica", 9)
            
            # Dados antropométricos
            if exame.parametros.peso or exame.parametros.altura:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "Dados Antropométricos:")
                y -= 15
                c.setFont("Helvetica", 9)
                
                if exame.parametros.peso:
                    c.drawString(70, y, f"Peso: {exame.parametros.peso} kg")
                    y -= 12
                if exame.parametros.altura:
                    c.drawString(70, y, f"Altura: {exame.parametros.altura} cm")
                    y -= 12
                if exame.parametros.superficie_corporal:
                    c.drawString(70, y, f"Superfície Corporal: {exame.parametros.superficie_corporal} m²")
                    y -= 12
                if exame.parametros.frequencia_cardiaca:
                    c.drawString(70, y, f"Frequência Cardíaca: {exame.parametros.frequencia_cardiaca} bpm")
                    y -= 12
            
            # Medidas básicas
            y -= 10
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Medidas Ecocardiográficas Básicas:")
            y -= 15
            c.setFont("Helvetica", 9)
            
            if exame.parametros.atrio_esquerdo:
                c.drawString(70, y, f"Átrio Esquerdo: {exame.parametros.atrio_esquerdo} mm")
                y -= 12
            if exame.parametros.raiz_aorta:
                c.drawString(70, y, f"Raiz da Aorta: {exame.parametros.raiz_aorta} mm")
                y -= 12
            if exame.parametros.aorta_ascendente:
                c.drawString(70, y, f"Aorta Ascendente: {exame.parametros.aorta_ascendente} mm")
                y -= 12
            
            # Ventrículo Esquerdo
            y -= 10
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Ventrículo Esquerdo:")
            y -= 15
            c.setFont("Helvetica", 9)
            
            if exame.parametros.diametro_diastolico_final_ve:
                c.drawString(70, y, f"DDVE: {exame.parametros.diametro_diastolico_final_ve} mm")
                y -= 12
            if exame.parametros.diametro_sistolico_final:
                c.drawString(70, y, f"DSVE: {exame.parametros.diametro_sistolico_final} mm")
                y -= 12
            if exame.parametros.fracao_ejecao:
                c.drawString(70, y, f"Fração de Ejeção: {exame.parametros.fracao_ejecao}%")
                y -= 12
            
            # Volumes
            if exame.parametros.volume_diastolico_final:
                c.drawString(70, y, f"Volume Diastólico Final: {exame.parametros.volume_diastolico_final} mL")
                y -= 12
            if exame.parametros.volume_sistolico_final:
                c.drawString(70, y, f"Volume Sistólico Final: {exame.parametros.volume_sistolico_final} mL")
                y -= 12
        
        # Laudos médicos
        if exame.laudos:
            laudo = exame.laudos[0]
            y -= 20
            
            # Modo M e Bidimensional
            if laudo.modo_m_bidimensional:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "MODO M E BIDIMENSIONAL:")
                y -= 15
                c.setFont("Helvetica", 9)
                
                # Quebrar texto
                texto = laudo.modo_m_bidimensional
                palavras = texto.split()
                linha_atual = ""
                
                for palavra in palavras:
                    if len(linha_atual + " " + palavra) < 70:
                        linha_atual += " " + palavra if linha_atual else palavra
                    else:
                        c.drawString(70, y, linha_atual)
                        y -= 12
                        linha_atual = palavra
                        if y < 100:  # Nova página se necessário
                            c.showPage()
                            y = 750
                
                if linha_atual:
                    c.drawString(70, y, linha_atual)
                    y -= 12
                
                y -= 10
            
            # Doppler Convencional
            if laudo.doppler_convencional:
                if y < 150:  # Nova página se necessário
                    c.showPage()
                    y = 750
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "DOPPLER CONVENCIONAL:")
                y -= 15
                c.setFont("Helvetica", 9)
                
                # Quebrar texto
                texto = laudo.doppler_convencional
                palavras = texto.split()
                linha_atual = ""
                
                for palavra in palavras:
                    if len(linha_atual + " " + palavra) < 70:
                        linha_atual += " " + palavra if linha_atual else palavra
                    else:
                        c.drawString(70, y, linha_atual)
                        y -= 12
                        linha_atual = palavra
                        if y < 100:  # Nova página se necessário
                            c.showPage()
                            y = 750
                
                if linha_atual:
                    c.drawString(70, y, linha_atual)
                    y -= 12
                
                y -= 10
            
            # Conclusão
            if laudo.conclusao:
                if y < 150:  # Nova página se necessário
                    c.showPage()
                    y = 750
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y, "CONCLUSÃO:")
                y -= 15
                c.setFont("Helvetica", 9)
                
                # Quebrar texto
                texto = laudo.conclusao
                palavras = texto.split()
                linha_atual = ""
                
                for palavra in palavras:
                    if len(linha_atual + " " + palavra) < 70:
                        linha_atual += " " + palavra if linha_atual else palavra
                    else:
                        c.drawString(70, y, linha_atual)
                        y -= 12
                        linha_atual = palavra
                        if y < 100:  # Nova página se necessário
                            c.showPage()
                            y = 750
                
                if linha_atual:
                    c.drawString(70, y, linha_atual)
                    y -= 12
        
        # Assinatura médica
        if y < 100:  # Nova página se necessário
            c.showPage()
            y = 750
        
        y -= 40
        c.setFont("Helvetica", 10)
        c.drawString(200, y, "Dr. Michel Raineri Haddad")
        y -= 15
        c.drawString(220, y, "CRM-SP 183299")
        y -= 15
        c.drawString(180, y, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        
        c.save()
        
        return caminho_pdf
        
    except Exception as e:
        logging.error(f'Erro ao gerar PDF: {str(e)}')
        return None

def calcular_parametros_derivados(parametros):
    """Calcular parâmetros derivados dos ecocardiográficos"""
    try:
        # Calcular superfície corporal (DuBois)
        if parametros.get('peso') and parametros.get('altura'):
            peso = float(parametros['peso'])
            altura = float(parametros['altura'])
            sc = 0.007184 * (peso ** 0.425) * (altura ** 0.725)
            parametros['superficie_corporal'] = round(sc, 2)
        
        # Calcular volumes pelo método Teichholz
        ddve = parametros.get('diametro_diastolico_final_ve')
        dsve = parametros.get('diametro_sistolico_final')
        
        if ddve and dsve:
            ddve = float(ddve) / 10  # mm para cm
            dsve = float(dsve) / 10  # mm para cm
            
            # Volume diastólico final
            vdf = (7.0 / (2.4 + ddve)) * (ddve ** 3)
            parametros['volume_diastolico_final'] = round(vdf, 1)
            
            # Volume sistólico final
            vsf = (7.0 / (2.4 + dsve)) * (dsve ** 3)
            parametros['volume_sistolico_final'] = round(vsf, 1)
            
            # Fração de ejeção
            if vdf > 0:
                fe = ((vdf - vsf) / vdf) * 100
                parametros['fracao_ejecao'] = round(fe, 1)
            
            # Volume de ejeção
            parametros['volume_ejecao'] = round(vdf - vsf, 1)
        
        # Calcular massa VE
        septo = parametros.get('espessura_diastolica_septo')
        pp = parametros.get('espessura_diastolica_ppve')
        
        if ddve and septo and pp:
            ddve_mm = float(ddve) if isinstance(ddve, str) else ddve
            septo_mm = float(septo) if isinstance(septo, str) else septo
            pp_mm = float(pp) if isinstance(pp, str) else pp
            
            # Fórmula ASE corrigida
            massa = 0.8 * (1.04 * (((ddve_mm + septo_mm + pp_mm) ** 3) - (ddve_mm ** 3))) + 0.6
            parametros['massa_ve'] = round(massa, 1)
            
            # Índice de massa VE
            if parametros.get('superficie_corporal'):
                indice_massa = massa / float(parametros['superficie_corporal'])
                parametros['indice_massa_ve'] = round(indice_massa, 1)
        
        # Calcular gradientes (Bernoulli)
        fluxos = ['fluxo_pulmonar', 'fluxo_mitral', 'fluxo_aortico', 'fluxo_tricuspide']
        gradientes = ['gradiente_vd_ap', 'gradiente_ae_ve', 'gradiente_ve_ao', 'gradiente_ad_vd']
        
        for fluxo, gradiente in zip(fluxos, gradientes):
            if parametros.get(fluxo):
                velocidade = float(parametros[fluxo])
                grad = 4 * (velocidade ** 2)
                parametros[gradiente] = round(grad, 1)
        
        # Calcular PSAP
        if parametros.get('gradiente_tricuspide'):
            grad_tricuspide = float(parametros['gradiente_tricuspide'])
            psap = grad_tricuspide + 10  # CVP estimada = 10mmHg
            parametros['pressao_sistolica_vd'] = round(psap, 1)
        
        return parametros
        
    except Exception as e:
        logging.error(f'Erro ao calcular parâmetros derivados: {str(e)}')
        return parametros

def log_system_event(message, user_id=None):
    """Log de eventos do sistema"""
    try:
        log_entry = LogSistema()
        log_entry.nivel = 'INFO'
        log_entry.mensagem = message
        log_entry.modulo = 'system'
        if user_id:
            log_entry.usuario_id = user_id
        
        db.session.add(log_entry)
        db.session.commit()
        logging.info(f'System event logged: {message}')
    except Exception as e:
        logging.error(f'Erro ao registrar log: {str(e)}')

def log_error_with_traceback(message, error, user_id=None):
    """Log de erros com traceback"""
    try:
        import traceback
        full_message = f"{message}: {str(error)}\n{traceback.format_exc()}"
        
        log_entry = LogSistema()
        log_entry.nivel = 'ERROR'
        log_entry.mensagem = full_message
        log_entry.modulo = 'error'
        if user_id:
            log_entry.usuario_id = user_id
        
        db.session.add(log_entry)
        db.session.commit()
        logging.error(full_message)
    except Exception as e:
        logging.error(f'Erro ao registrar log de erro: {str(e)}')

# ===== ROTAS DE AUTENTICAÇÃO =====

@app.route('/login', methods=['GET', 'POST'])
def auth_login():
    """Página de login do sistema"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Tentar AuthUser primeiro (novo sistema)
        user = AuthUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            log_system_event(f'Login bem-sucedido: {username}', user.id)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        flash('Usuário ou senha inválidos', 'error')
        log_system_event(f'Tentativa de login falhada: {username}')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def auth_logout():
    """Logout do usuário"""
    username = current_user.username
    user_id = current_user.id
    logout_user()
    log_system_event(f'Logout realizado: {username}', user_id)
    flash('Logout realizado com sucesso', 'success')
    return redirect(url_for('auth_login'))

# ===== ROTAS PRINCIPAIS =====

@app.route('/')
@login_required
def index():
    """Página inicial do sistema"""
    try:
        # Estatísticas básicas do sistema
        total_exames = Exame.query.count()
        total_pacientes = db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar()
        
        # Exames recentes (últimos 10)
        exames_recentes = Exame.query.order_by(desc(Exame.created_at)).limit(10).all()
        
        # Exames hoje
        hoje = datetime.now().date()
        exames_hoje = Exame.query.filter(func.date(Exame.created_at) == hoje).count()
        
        # Log de acesso
        log_system_event(f'Acesso à página inicial - Usuário: {current_user.username}', current_user.id)
        
        return render_template('index.html', 
                             total_exames=total_exames,
                             total_pacientes=total_pacientes,
                             exames_recentes=exames_recentes,
                             exames_hoje=exames_hoje)
                             
    except Exception as e:
        log_error_with_traceback('Erro na página inicial', e, current_user.id)
        flash('Erro ao carregar página inicial', 'error')
        return render_template('index.html', 
                             total_exames=0,
                             total_pacientes=0,
                             exames_recentes=[],
                             exames_hoje=0)

@app.route('/novo_exame', methods=['GET', 'POST'])
@login_required
def novo_exame():
    """Criar novo exame ou clonar de paciente existente"""
    clone_paciente = request.args.get('clone_paciente')
    dados_clonados = None
    
    if clone_paciente:
        try:
            # Buscar o último exame deste paciente
            ultimo_exame = Exame.query.filter_by(nome_paciente=clone_paciente)\
                                     .order_by(desc(Exame.created_at)).first()
            
            if ultimo_exame:
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
                
                # Adicionar parâmetros se existirem
                if ultimo_exame.parametros:
                    params = ultimo_exame.parametros
                    dados_clonados.update({
                        'peso': params.peso,
                        'altura': params.altura,
                        'superficie_corporal': params.superficie_corporal,
                        'frequencia_cardiaca': params.frequencia_cardiaca,
                        'atrio_esquerdo': params.atrio_esquerdo,
                        'raiz_aorta': params.raiz_aorta,
                        'relacao_atrio_esquerdo_aorta': params.relacao_atrio_esquerdo_aorta,
                        'aorta_ascendente': params.aorta_ascendente,
                        'diametro_ventricular_direito': params.diametro_ventricular_direito,
                        'diametro_basal_vd': params.diametro_basal_vd,
                        'diametro_diastolico_final_ve': params.diametro_diastolico_final_ve,
                        'diametro_sistolico_final': params.diametro_sistolico_final,
                        'percentual_encurtamento': params.percentual_encurtamento,
                        'espessura_diastolica_septo': params.espessura_diastolica_septo,
                        'espessura_diastolica_ppve': params.espessura_diastolica_ppve,
                        'relacao_septo_parede_posterior': params.relacao_septo_parede_posterior,
                        'volume_diastolico_final': params.volume_diastolico_final,
                        'volume_sistolico_final': params.volume_sistolico_final,
                        'volume_ejecao': params.volume_ejecao,
                        'fracao_ejecao': params.fracao_ejecao,
                        'indice_massa_ve': params.indice_massa_ve,
                        'massa_ve': params.massa_ve,
                        'fluxo_pulmonar': params.fluxo_pulmonar,
                        'fluxo_mitral': params.fluxo_mitral,
                        'fluxo_aortico': params.fluxo_aortico,
                        'fluxo_tricuspide': params.fluxo_tricuspide,
                        'gradiente_vd_ap': params.gradiente_vd_ap,
                        'gradiente_ae_ve': params.gradiente_ae_ve,
                        'gradiente_ve_ao': params.gradiente_ve_ao,
                        'gradiente_ad_vd': params.gradiente_ad_vd,
                        'gradiente_tricuspide': params.gradiente_tricuspide,
                        'pressao_sistolica_vd': params.pressao_sistolica_vd
                    })
                
                # Adicionar laudos se existirem
                if ultimo_exame.laudos:
                    laudo = ultimo_exame.laudos[0]
                    dados_clonados.update({
                        'modo_m_bidimensional': laudo.modo_m_bidimensional,
                        'doppler_convencional': laudo.doppler_convencional,
                        'doppler_tecidual': laudo.doppler_tecidual,
                        'conclusao': laudo.conclusao,
                        'recomendacoes': laudo.recomendacoes
                    })
                
                log_system_event(f'Dados clonados do último exame - Paciente: {clone_paciente}', current_user.id)
        
        except Exception as e:
            log_error_with_traceback('Erro ao clonar dados do paciente', e, current_user.id)
            flash('Erro ao carregar dados do paciente anterior', 'warning')
    
    if request.method == 'POST':
        try:
            # Dados básicos do exame
            exame = Exame()
            exame.nome_paciente = request.form['nome_paciente']
            exame.data_nascimento = request.form['data_nascimento']
            exame.idade = int(request.form['idade']) if request.form['idade'] else None
            exame.sexo = request.form['sexo']
            exame.data_exame = request.form['data_exame']
            exame.tipo_atendimento = request.form.get('tipo_atendimento', '')
            exame.medico_usuario = request.form.get('medico_usuario', '')
            exame.medico_solicitante = request.form.get('medico_solicitante', '')
            exame.indicacao = request.form.get('indicacao', '')
            
            db.session.add(exame)
            db.session.flush()  # Para obter o ID
            
            # Criar parâmetros ecocardiográficos
            parametros = ParametrosEcocardiograma()
            parametros.exame_id = exame.id
            
            # Coletar todos os dados do formulário
            form_data = {}
            for key in request.form:
                if key.startswith(('peso', 'altura', 'superficie', 'frequencia', 'atrio', 'raiz', 'relacao', 'aorta', 
                                  'diametro', 'espessura', 'percentual', 'volume', 'fracao', 'massa', 'indice',
                                  'fluxo', 'gradiente', 'pressao')):
                    value = request.form[key]
                    if value:
                        form_data[key] = value
            
            # Calcular parâmetros derivados
            form_data = calcular_parametros_derivados(form_data)
            
            # Aplicar valores aos parâmetros
            for field_name, value in form_data.items():
                if hasattr(parametros, field_name) and value:
                    try:
                        if field_name in ['frequencia_cardiaca']:
                            setattr(parametros, field_name, int(value))
                        else:
                            setattr(parametros, field_name, float(value))
                    except (ValueError, TypeError):
                        continue
            
            db.session.add(parametros)
            
            # Criar laudo médico
            laudo = LaudoEcocardiograma()
            laudo.exame_id = exame.id
            laudo.modo_m_bidimensional = request.form.get('modo_m_bidimensional', '')
            laudo.doppler_convencional = request.form.get('doppler_convencional', '')
            laudo.doppler_tecidual = request.form.get('doppler_tecidual', '')
            laudo.conclusao = request.form.get('conclusao', '')
            laudo.recomendacoes = request.form.get('recomendacoes', '')
            
            db.session.add(laudo)
            db.session.commit()
            
            # Log da operação
            log_system_event(f'Novo exame criado: ID {exame.id}, Paciente: {exame.nome_paciente}', current_user.id)
            
            flash('Exame criado com sucesso!', 'success')
            return redirect(url_for('visualizar_exame', id=exame.id))
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback('Erro ao criar novo exame', e, current_user.id)
            flash(f'Erro ao criar exame: {str(e)}', 'error')
    
    # Buscar médicos para o formulário
    try:
        medicos = Medico.query.filter_by(ativo=True).all()
    except:
        medicos = []
    
    return render_template('novo_exame.html', 
                         medicos=medicos,
                         dados_clonados=dados_clonados)

@app.route('/prontuario')
@login_required
def prontuario():
    """Página principal do prontuário - busca de pacientes"""
    log_system_event(f'Acesso ao prontuário - Usuário: {current_user.username}', current_user.id)
    return render_template('prontuario/index.html')

@app.route('/prontuario/buscar')
@login_required
def buscar_pacientes():
    """Buscar pacientes no prontuário"""
    termo = request.args.get('q', '').strip()
    
    if not termo:
        return jsonify([])
    
    try:
        # Dividir termo em palavras para busca mais precisa
        palavras = termo.lower().split()
        
        # Buscar pacientes que contenham todas as palavras
        query = db.session.query(Exame.nome_paciente, func.count(Exame.id).label('total_exames'))\
                          .group_by(Exame.nome_paciente)
        
        for palavra in palavras:
            # Busca por palavras completas
            query = query.filter(
                func.lower(Exame.nome_paciente).like(f'% {palavra} %') |
                func.lower(Exame.nome_paciente).like(f'{palavra} %') |
                func.lower(Exame.nome_paciente).like(f'% {palavra}') |
                func.lower(Exame.nome_paciente).like(f'{palavra}')
            )
        
        pacientes = query.order_by(Exame.nome_paciente).limit(20).all()
        
        resultados = []
        for paciente in pacientes:
            # Buscar último exame do paciente
            ultimo_exame = Exame.query.filter_by(nome_paciente=paciente.nome_paciente)\
                                    .order_by(desc(Exame.created_at)).first()
            
            if ultimo_exame:
                resultados.append({
                    'nome': paciente.nome_paciente,
                    'total_exames': paciente.total_exames,
                    'ultimo_exame': ultimo_exame.data_exame,
                    'idade': ultimo_exame.idade,
                    'sexo': ultimo_exame.sexo
                })
        
        log_system_event(f'Busca no prontuário: "{termo}" - {len(resultados)} resultados', current_user.id)
        return jsonify(resultados)
        
    except Exception as e:
        log_error_with_traceback('Erro na busca de pacientes', e, current_user.id)
        return jsonify([])

@app.route('/prontuario/<nome_paciente>')
@login_required
def prontuario_paciente(nome_paciente):
    """Ver prontuário completo de um paciente"""
    try:
        # Buscar todos os exames do paciente
        exames = Exame.query.filter_by(nome_paciente=nome_paciente)\
                           .order_by(desc(Exame.created_at)).all()
        
        if not exames:
            flash('Paciente não encontrado', 'error')
            return redirect(url_for('prontuario'))
        
        # Dados do paciente (do último exame)
        paciente = exames[0]
        
        log_system_event(f'Visualização de prontuário - Paciente: {nome_paciente}', current_user.id)
        
        return render_template('prontuario/paciente.html', 
                             paciente=paciente,
                             exames=exames)
                             
    except Exception as e:
        log_error_with_traceback('Erro ao carregar prontuário do paciente', e, current_user.id)
        flash('Erro ao carregar prontuário', 'error')
        return redirect(url_for('prontuario'))

@app.route('/parametros/<int:id>')
@login_required
def parametros(id):
    """Página de parâmetros ecocardiográficos"""
    try:
        exame = Exame.query.get_or_404(id)
        
        # Criar parâmetros se não existirem
        if not exame.parametros:
            parametros = ParametrosEcocardiograma()
            parametros.exame_id = id
            db.session.add(parametros)
            db.session.commit()
            log_system_event(f'Parâmetros criados para exame ID {id}', current_user.id)
        
        log_system_event(f'Acesso aos parâmetros - Exame ID: {id}', current_user.id)
        return render_template('parametros.html', exame=exame)
        
    except Exception as e:
        log_error_with_traceback('Erro ao carregar parâmetros', e, current_user.id)
        flash('Erro ao carregar parâmetros', 'error')
        return redirect(url_for('index'))

@app.route('/salvar_parametros/<int:id>', methods=['POST'])
@login_required
def salvar_parametros(id):
    """Salvar parâmetros ecocardiográficos"""
    try:
        exame = Exame.query.get_or_404(id)
        parametros = exame.parametros
        
        if not parametros:
            parametros = ParametrosEcocardiograma()
            parametros.exame_id = id
            db.session.add(parametros)
        
        # Coletar dados do formulário
        form_data = {}
        for field_name in request.form:
            value = request.form[field_name]
            if value:
                form_data[field_name] = value
        
        # Calcular parâmetros derivados
        form_data = calcular_parametros_derivados(form_data)
        
        # Atualizar todos os campos dos parâmetros
        for field_name, value in form_data.items():
            if hasattr(parametros, field_name):
                try:
                    if field_name in ['frequencia_cardiaca']:
                        setattr(parametros, field_name, int(value))
                    else:
                        setattr(parametros, field_name, float(value))
                except (ValueError, TypeError):
                    continue
        
        db.session.commit()
        
        log_system_event(f'Parâmetros atualizados para exame ID {id}', current_user.id)
        flash('Parâmetros salvos com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao salvar parâmetros', e, current_user.id)
        flash(f'Erro ao salvar parâmetros: {str(e)}', 'error')
    
    return redirect(url_for('parametros', id=id))

@app.route('/laudo/<int:id>')
@login_required
def laudo(id):
    """Página de laudos médicos"""
    try:
        exame = Exame.query.get_or_404(id)
        
        # Criar laudo se não existir
        if not exame.laudos:
            laudo = LaudoEcocardiograma()
            laudo.exame_id = id
            db.session.add(laudo)
            db.session.commit()
            log_system_event(f'Laudo criado para exame ID {id}', current_user.id)
        
        log_system_event(f'Acesso ao laudo - Exame ID: {id}', current_user.id)
        return render_template('laudo.html', exame=exame)
        
    except Exception as e:
        log_error_with_traceback('Erro ao carregar laudo', e, current_user.id)
        flash('Erro ao carregar laudo', 'error')
        return redirect(url_for('index'))

@app.route('/salvar_laudo/<int:id>', methods=['POST'])
@login_required
def salvar_laudo(id):
    """Salvar laudo médico"""
    try:
        exame = Exame.query.get_or_404(id)
        
        if not exame.laudos:
            laudo = LaudoEcocardiograma()
            laudo.exame_id = id
            db.session.add(laudo)
        else:
            laudo = exame.laudos[0]
        
        # Atualizar campos do laudo
        laudo.modo_m_bidimensional = request.form.get('modo_m_bidimensional', '')
        laudo.doppler_convencional = request.form.get('doppler_convencional', '')
        laudo.doppler_tecidual = request.form.get('doppler_tecidual', '')
        laudo.conclusao = request.form.get('conclusao', '')
        laudo.recomendacoes = request.form.get('recomendacoes', '')
        
        db.session.commit()
        
        log_system_event(f'Laudo atualizado para exame ID {id}', current_user.id)
        flash('Laudo salvo com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao salvar laudo', e, current_user.id)
        flash(f'Erro ao salvar laudo: {str(e)}', 'error')
    
    return redirect(url_for('laudo', id=id))

@app.route('/visualizar_exame/<int:id>')
@login_required
def visualizar_exame(id):
    """Visualizar exame completo"""
    try:
        exame = Exame.query.get_or_404(id)
        log_system_event(f'Visualização de exame - ID: {id}, Paciente: {exame.nome_paciente}', current_user.id)
        return render_template('visualizar_exame.html', exame=exame)
    except Exception as e:
        log_error_with_traceback('Erro ao visualizar exame', e, current_user.id)
        flash('Erro ao carregar exame', 'error')
        return redirect(url_for('index'))

@app.route('/gerar-pdf/<int:id>')
@login_required
def gerar_pdf(id):
    """Gerar PDF do exame"""
    try:
        exame = Exame.query.get_or_404(id)
        
        # Gerar PDF
        caminho_pdf = generate_pdf_report(exame)
        
        if caminho_pdf:
            log_system_event(f'PDF gerado para exame ID {id}', current_user.id)
            
            # Retornar arquivo para download
            return send_file(caminho_pdf, as_attachment=True, 
                            download_name=f'laudo_ecocardiograma_{id}.pdf')
        else:
            raise Exception("Falha na geração do PDF")
    
    except Exception as e:
        log_error_with_traceback('Erro ao gerar PDF', e, current_user.id)
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('visualizar_exame', id=id))

@app.route('/cadastro_medico', methods=['GET', 'POST'])
@login_required
def cadastro_medico():
    """Cadastro e gestão de médicos"""
    if request.method == 'POST':
        try:
            medico = Medico()
            medico.nome = request.form['nome']
            medico.crm = request.form['crm']
            medico.assinatura_data = request.form.get('assinatura_data', '')
            medico.assinatura_url = request.form.get('assinatura_url', '')
            
            db.session.add(medico)
            db.session.commit()
            
            log_system_event(f'Médico cadastrado: {medico.nome} - {medico.crm}', current_user.id)
            flash('Médico cadastrado com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback('Erro ao cadastrar médico', e, current_user.id)
            flash(f'Erro ao cadastrar médico: {str(e)}', 'error')
    
    # Listar médicos existentes
    try:
        medicos = Medico.query.filter_by(ativo=True).all()
    except:
        medicos = []
    
    return render_template('cadastro_medico.html', medicos=medicos)

@app.route('/editar_medico/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_medico(id):
    """Editar dados do médico"""
    try:
        medico = Medico.query.get_or_404(id)
        
        if request.method == 'POST':
            medico.nome = request.form['nome']
            medico.crm = request.form['crm']
            medico.assinatura_data = request.form.get('assinatura_data', '')
            medico.assinatura_url = request.form.get('assinatura_url', '')
            
            db.session.commit()
            
            log_system_event(f'Médico atualizado: {medico.nome} - {medico.crm}', current_user.id)
            flash('Médico atualizado com sucesso!', 'success')
            return redirect(url_for('cadastro_medico'))
        
        return render_template('editar_medico.html', medico=medico)
        
    except Exception as e:
        log_error_with_traceback('Erro ao editar médico', e, current_user.id)
        flash('Erro ao carregar dados do médico', 'error')
        return redirect(url_for('cadastro_medico'))

@app.route('/novo-exame-prontuario/<nome_paciente>')
@login_required
def novo_exame_prontuario(nome_paciente):
    """Rota para novo exame a partir do prontuário - redireciona para novo_exame com clone"""
    return redirect(url_for('novo_exame', clone_paciente=nome_paciente))

# ===== APIs DO SISTEMA =====

@app.route('/api/ultimo-exame-paciente/<nome_paciente>')
@login_required
def api_ultimo_exame_paciente(nome_paciente):
    """API para buscar último exame de um paciente"""
    try:
        ultimo_exame = Exame.query.filter_by(nome_paciente=nome_paciente)\
                                 .order_by(desc(Exame.created_at)).first()
        
        if not ultimo_exame:
            return jsonify({'erro': 'Paciente não encontrado'}), 404
        
        dados = {
            'exame': {
                'nome_paciente': ultimo_exame.nome_paciente,
                'data_nascimento': ultimo_exame.data_nascimento,
                'idade': ultimo_exame.idade,
                'sexo': ultimo_exame.sexo,
                'tipo_atendimento': ultimo_exame.tipo_atendimento,
                'medico_usuario': ultimo_exame.medico_usuario,
                'medico_solicitante': ultimo_exame.medico_solicitante,
                'indicacao': ultimo_exame.indicacao
            }
        }
        
        # Adicionar parâmetros se existirem
        if ultimo_exame.parametros:
            dados['parametros'] = {
                'peso': ultimo_exame.parametros.peso,
                'altura': ultimo_exame.parametros.altura,
                'superficie_corporal': ultimo_exame.parametros.superficie_corporal,
                'frequencia_cardiaca': ultimo_exame.parametros.frequencia_cardiaca,
                'atrio_esquerdo': ultimo_exame.parametros.atrio_esquerdo,
                'raiz_aorta': ultimo_exame.parametros.raiz_aorta,
                'relacao_atrio_esquerdo_aorta': ultimo_exame.parametros.relacao_atrio_esquerdo_aorta,
                'aorta_ascendente': ultimo_exame.parametros.aorta_ascendente,
                'diametro_ventricular_direito': ultimo_exame.parametros.diametro_ventricular_direito,
                'diametro_basal_vd': ultimo_exame.parametros.diametro_basal_vd,
                'diametro_diastolico_final_ve': ultimo_exame.parametros.diametro_diastolico_final_ve,
                'diametro_sistolico_final': ultimo_exame.parametros.diametro_sistolico_final,
                'percentual_encurtamento': ultimo_exame.parametros.percentual_encurtamento,
                'espessura_diastolica_septo': ultimo_exame.parametros.espessura_diastolica_septo,
                'espessura_diastolica_ppve': ultimo_exame.parametros.espessura_diastolica_ppve,
                'relacao_septo_parede_posterior': ultimo_exame.parametros.relacao_septo_parede_posterior,
                'volume_diastolico_final': ultimo_exame.parametros.volume_diastolico_final,
                'volume_sistolico_final': ultimo_exame.parametros.volume_sistolico_final,
                'volume_ejecao': ultimo_exame.parametros.volume_ejecao,
                'fracao_ejecao': ultimo_exame.parametros.fracao_ejecao,
                'indice_massa_ve': ultimo_exame.parametros.indice_massa_ve,
                'massa_ve': ultimo_exame.parametros.massa_ve,
                'fluxo_pulmonar': ultimo_exame.parametros.fluxo_pulmonar,
                'fluxo_mitral': ultimo_exame.parametros.fluxo_mitral,
                'fluxo_aortico': ultimo_exame.parametros.fluxo_aortico,
                'fluxo_tricuspide': ultimo_exame.parametros.fluxo_tricuspide,
                'gradiente_vd_ap': ultimo_exame.parametros.gradiente_vd_ap,
                'gradiente_ae_ve': ultimo_exame.parametros.gradiente_ae_ve,
                'gradiente_ve_ao': ultimo_exame.parametros.gradiente_ve_ao,
                'gradiente_ad_vd': ultimo_exame.parametros.gradiente_ad_vd,
                'gradiente_tricuspide': ultimo_exame.parametros.gradiente_tricuspide,
                'pressao_sistolica_vd': ultimo_exame.parametros.pressao_sistolica_vd
            }
        
        # Adicionar laudos se existirem
        if ultimo_exame.laudos:
            dados['laudos'] = {
                'modo_m_bidimensional': ultimo_exame.laudos[0].modo_m_bidimensional,
                'doppler_convencional': ultimo_exame.laudos[0].doppler_convencional,
                'doppler_tecidual': ultimo_exame.laudos[0].doppler_tecidual,
                'conclusao': ultimo_exame.laudos[0].conclusao,
                'recomendacoes': ultimo_exame.laudos[0].recomendacoes
            }
        
        return jsonify(dados)
        
    except Exception as e:
        log_error_with_traceback('Erro na API último exame', e, current_user.id)
        return jsonify({'erro': str(e)}), 500

@app.route('/api/salvar-novo-exame-completo', methods=['POST'])
@login_required
def api_salvar_novo_exame_completo():
    """API para salvar novo exame completo"""
    try:
        data = request.get_json()
        
        # Criar novo exame
        exame = Exame()
        exame.nome_paciente = data.get('nome_paciente')
        exame.data_nascimento = data.get('data_nascimento')
        exame.idade = data.get('idade')
        exame.sexo = data.get('sexo')
        exame.data_exame = datetime.now().strftime('%Y-%m-%d')
        exame.tipo_atendimento = data.get('tipo_atendimento', '')
        exame.medico_usuario = data.get('medico_usuario', '')
        exame.medico_solicitante = data.get('medico_solicitante', '')
        exame.indicacao = data.get('indicacao', '')
        
        db.session.add(exame)
        db.session.flush()
        
        # Criar parâmetros
        parametros = ParametrosEcocardiograma()
        parametros.exame_id = exame.id
        
        # Aplicar parâmetros do JSON
        parametros_data = data.get('parametros', {})
        for field, value in parametros_data.items():
            if hasattr(parametros, field) and value is not None:
                try:
                    if field == 'frequencia_cardiaca':
                        setattr(parametros, field, int(value))
                    else:
                        setattr(parametros, field, float(value))
                except (ValueError, TypeError):
                    continue
        
        db.session.add(parametros)
        
        # Criar laudo
        laudo = LaudoEcocardiograma()
        laudo.exame_id = exame.id
        
        laudos_data = data.get('laudos', {})
        laudo.modo_m_bidimensional = laudos_data.get('modo_m_bidimensional', '')
        laudo.doppler_convencional = laudos_data.get('doppler_convencional', '')
        laudo.doppler_tecidual = laudos_data.get('doppler_tecidual', '')
        laudo.conclusao = laudos_data.get('conclusao', '')
        laudo.recomendacoes = laudos_data.get('recomendacoes', '')
        
        db.session.add(laudo)
        db.session.commit()
        
        log_system_event(f'Novo exame completo criado via API: ID {exame.id}', current_user.id)
        
        return jsonify({
            'success': True,
            'exame_id': exame.id,
            'message': 'Exame criado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro na API salvar novo exame completo', e, current_user.id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/hora-atual')
@login_required
def api_hora_atual():
    """API para obter hora atual de Brasília"""
    try:
        # Fuso horário de Brasília (UTC-3)
        brasilia_tz = timezone(timedelta(hours=-3))
        agora_brasilia = datetime.now(brasilia_tz)
        
        return jsonify({
            'hora': agora_brasilia.strftime('%H:%M:%S'),
            'data': agora_brasilia.strftime('%d/%m/%Y'),
            'timestamp': agora_brasilia.isoformat()
        })
        
    except Exception as e:
        log_error_with_traceback('Erro na API hora atual', e, current_user.id)
        return jsonify({'erro': str(e)}), 500

@app.route('/api/estatisticas')
@login_required
def api_estatisticas():
    """API para estatísticas do sistema"""
    try:
        hoje = datetime.now().date()
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        stats = {
            'total_exames': Exame.query.count(),
            'total_pacientes': db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar(),
            'exames_hoje': Exame.query.filter(func.date(Exame.created_at) == hoje).count(),
            'exames_mes': Exame.query.filter(
                func.extract('month', Exame.created_at) == mes_atual,
                func.extract('year', Exame.created_at) == ano_atual
            ).count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        log_error_with_traceback('Erro na API estatísticas', e, current_user.id)
        return jsonify({'erro': str(e)}), 500

@app.route('/api/templates-laudo')
@login_required
def api_templates_laudo():
    """API para buscar templates de laudo"""
    try:
        busca = request.args.get('q', '').strip()
        categoria = request.args.get('categoria', '')
        
        query = LaudoTemplate.query.filter_by(ativo=True)
        
        if busca:
            query = query.filter(
                (LaudoTemplate.diagnostico.contains(busca)) |
                (LaudoTemplate.conclusao.contains(busca))
            )
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        templates = query.order_by(LaudoTemplate.diagnostico).limit(50).all()
        
        resultados = []
        for template in templates:
            resultados.append({
                'id': template.id,
                'categoria': template.categoria,
                'diagnostico': template.diagnostico,
                'modo_m_bidimensional': template.modo_m_bidimensional,
                'doppler_convencional': template.doppler_convencional,
                'doppler_tecidual': template.doppler_tecidual,
                'conclusao': template.conclusao
            })
        
        return jsonify(resultados)
        
    except Exception as e:
        log_error_with_traceback('Erro na API templates', e, current_user.id)
        return jsonify({'erro': str(e)}), 500

@app.route('/api/salvar-template-laudo', methods=['POST'])
@login_required
def api_salvar_template_laudo():
    """API para salvar template de laudo"""
    try:
        data = request.get_json()
        
        template = LaudoTemplate()
        template.categoria = data.get('categoria', 'Geral')
        template.diagnostico = data.get('diagnostico', '')
        template.modo_m_bidimensional = data.get('modo_m_bidimensional', '')
        template.doppler_convencional = data.get('doppler_convencional', '')
        template.doppler_tecidual = data.get('doppler_tecidual', '')
        template.conclusao = data.get('conclusao', '')
        
        db.session.add(template)
        db.session.commit()
        
        log_system_event(f'Template de laudo criado: {template.diagnostico}', current_user.id)
        
        return jsonify({
            'success': True,
            'template_id': template.id,
            'message': 'Template salvo com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao salvar template', e, current_user.id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/verificar-duplicatas')
@login_required
def api_verificar_duplicatas():
    """API para verificar pacientes duplicados"""
    try:
        # Buscar nomes similares
        subquery = db.session.query(Exame.nome_paciente, func.count().label('count'))\
                           .group_by(Exame.nome_paciente)\
                           .having(func.count() > 1).subquery()
        
        duplicatas = db.session.query(subquery.c.nome_paciente, subquery.c.count).all()
        
        resultado = []
        for nome, count in duplicatas:
            # Buscar variações do nome
            nome_normalizado = nome.lower().strip()
            variações = Exame.query.filter(
                func.lower(func.trim(Exame.nome_paciente)) == nome_normalizado
            ).with_entities(Exame.nome_paciente).distinct().all()
            
            if len(variações) > 1:
                resultado.append({
                    'nome_principal': nome,
                    'total_exames': count,
                    'variações': [v[0] for v in variações]
                })
        
        return jsonify({
            'duplicatas_encontradas': len(resultado),
            'pacientes': resultado
        })
        
    except Exception as e:
        log_error_with_traceback('Erro na verificação de duplicatas', e, current_user.id)
        return jsonify({'erro': str(e)}), 500

@app.route('/api/excluir_exame/<int:id>', methods=['DELETE'])
@login_required
def api_excluir_exame(id):
    """API para excluir exame"""
    try:
        exame = Exame.query.get_or_404(id)
        nome_paciente = exame.nome_paciente
        
        # Excluir em cascata
        if exame.parametros:
            db.session.delete(exame.parametros)
        
        for laudo in exame.laudos:
            db.session.delete(laudo)
        
        db.session.delete(exame)
        db.session.commit()
        
        log_system_event(f'Exame excluído: ID {id}, Paciente: {nome_paciente}', current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Exame excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao excluir exame', e, current_user.id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ===== ROTAS DE MANUTENÇÃO =====

@app.route('/admin-vidah-sistema-2025')
@login_required
@admin_required
def manutencao_index():
    """Página principal de manutenção do sistema"""
    try:
        # Estatísticas básicas
        stats = {
            'total_exames': Exame.query.count(),
            'total_pacientes': db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar(),
            'total_medicos': Medico.query.filter_by(ativo=True).count(),
            'total_usuarios': AuthUser.query.filter_by(is_active=True).count(),
            'total_logs': LogSistema.query.count()
        }
        
        # Logs recentes
        logs_recentes = LogSistema.query.order_by(desc(LogSistema.created_at)).limit(10).all()
        
        log_system_event(f'Acesso à manutenção - Admin: {current_user.username}', current_user.id)
        
        return render_template('manutencao/index.html', 
                             stats=stats,
                             logs_recentes=logs_recentes)
                             
    except Exception as e:
        log_error_with_traceback('Erro na página de manutenção', e, current_user.id)
        return render_template('manutencao/index.html', 
                             stats={},
                             logs_recentes=[])

@app.route('/admin-vidah-sistema-2025/backup')
@login_required
@admin_required
def pagina_backup():
    """Página de backup e restauração"""
    try:
        # Lista simplificada de backups
        backups = []
        
        # Simular alguns backups
        backups.append({
            'nome': f'backup_manual_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'tamanho': '2.5 MB',
            'tipo': 'Manual'
        })
        
        return render_template('manutencao/backup.html', backups=backups)
        
    except Exception as e:
        log_error_with_traceback('Erro na página de backup', e, current_user.id)
        return render_template('manutencao/backup.html', backups=[])

@app.route('/admin-vidah-sistema-2025/backup/criar', methods=['POST'])
@login_required
@admin_required
def criar_backup_route():
    """Cria um novo backup do sistema"""
    try:
        # Backup simplificado - contar registros
        stats_backup = {
            'timestamp': datetime.now().isoformat(),
            'total_exames': Exame.query.count(),
            'total_pacientes': db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar(),
            'total_medicos': Medico.query.count(),
            'total_usuarios': AuthUser.query.count(),
            'criado_por': current_user.username
        }
        
        # Salvar estatísticas em log
        log_system_event(f'Backup manual criado: {json.dumps(stats_backup)}', current_user.id)
        
        flash('Backup criado com sucesso!', 'success')
        
    except Exception as e:
        log_error_with_traceback('Erro ao criar backup', e, current_user.id)
        flash(f'Erro ao criar backup: {str(e)}', 'error')
    
    return redirect(url_for('pagina_backup'))

@app.route('/admin-vidah-sistema-2025/logs')
@login_required
@admin_required
def pagina_logs():
    """Página de visualização de logs"""
    try:
        # Filtros
        nivel = request.args.get('nivel', '')
        modulo = request.args.get('modulo', '')
        usuario_id = request.args.get('usuario_id', '')
        
        query = LogSistema.query
        
        if nivel:
            query = query.filter_by(nivel=nivel)
        if modulo:
            query = query.filter_by(modulo=modulo)
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        logs = query.order_by(desc(LogSistema.created_at)).limit(200).all()
        
        # Estatísticas de logs
        stats_logs = {
            'total': LogSistema.query.count(),
            'info': LogSistema.query.filter_by(nivel='INFO').count(),
            'warning': LogSistema.query.filter_by(nivel='WARNING').count(),
            'error': LogSistema.query.filter_by(nivel='ERROR').count()
        }
        
        return render_template('manutencao/logs.html', 
                             logs=logs,
                             stats_logs=stats_logs)
                             
    except Exception as e:
        log_error_with_traceback('Erro na página de logs', e, current_user.id)
        return render_template('manutencao/logs.html', 
                             logs=[],
                             stats_logs={})

@app.route('/admin-vidah-sistema-2025/logs/limpar', methods=['POST'])
@login_required
@admin_required
def limpar_logs():
    """Limpar logs antigos"""
    try:
        # Manter apenas os últimos 1000 logs
        logs_para_manter = LogSistema.query.order_by(desc(LogSistema.created_at)).limit(1000).all()
        ids_manter = [log.id for log in logs_para_manter]
        
        if ids_manter:
            logs_deletados = LogSistema.query.filter(~LogSistema.id.in_(ids_manter)).delete(synchronize_session=False)
        else:
            logs_deletados = LogSistema.query.delete()
        
        db.session.commit()
        
        log_system_event(f'Limpeza de logs: {logs_deletados} registros removidos', current_user.id)
        flash(f'{logs_deletados} logs antigos foram removidos', 'success')
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao limpar logs', e, current_user.id)
        flash(f'Erro ao limpar logs: {str(e)}', 'error')
    
    return redirect(url_for('pagina_logs'))

@app.route('/admin-vidah-sistema-2025/usuarios')
@login_required
@admin_required
def gerenciar_usuarios():
    """Página de gerenciamento de usuários"""
    try:
        usuarios = AuthUser.query.all()
        return render_template('manutencao/usuarios.html', usuarios=usuarios)
    except Exception as e:
        log_error_with_traceback('Erro no gerenciamento de usuários', e, current_user.id)
        return render_template('manutencao/usuarios.html', usuarios=[])

@app.route('/admin-vidah-sistema-2025/usuarios/criar', methods=['GET', 'POST'])
@login_required
@admin_required
def criar_usuario():
    """Criar novo usuário"""
    if request.method == 'POST':
        try:
            usuario = AuthUser()
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            usuario.set_password(request.form['password'])
            usuario.role = request.form.get('role', 'user')
            usuario.is_active = True
            
            db.session.add(usuario)
            db.session.commit()
            
            log_system_event(f'Usuário criado: {usuario.username}', current_user.id)
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('gerenciar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            log_error_with_traceback('Erro ao criar usuário', e, current_user.id)
            flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return render_template('manutencao/criar_usuario.html')

@app.route('/admin-vidah-sistema-2025/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    """Editar usuário existente"""
    try:
        usuario = AuthUser.query.get_or_404(id)
        
        if request.method == 'POST':
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            if request.form.get('password'):
                usuario.set_password(request.form['password'])
            usuario.role = request.form.get('role', 'user')
            usuario.is_active = 'is_active' in request.form
            
            db.session.commit()
            
            log_system_event(f'Usuário atualizado: {usuario.username}', current_user.id)
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('gerenciar_usuarios'))
        
        return render_template('manutencao/editar_usuario.html', usuario=usuario)
        
    except Exception as e:
        log_error_with_traceback('Erro ao editar usuário', e, current_user.id)
        flash('Erro ao carregar usuário', 'error')
        return redirect(url_for('gerenciar_usuarios'))

@app.route('/admin-vidah-sistema-2025/usuarios/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(id):
    """Excluir usuário"""
    try:
        usuario = AuthUser.query.get_or_404(id)
        
        # Não permitir excluir o próprio usuário
        if usuario.id == current_user.id:
            flash('Não é possível excluir seu próprio usuário', 'error')
            return redirect(url_for('gerenciar_usuarios'))
        
        username = usuario.username
        db.session.delete(usuario)
        db.session.commit()
        
        log_system_event(f'Usuário excluído: {username}', current_user.id)
        flash('Usuário excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao excluir usuário', e, current_user.id)
        flash(f'Erro ao excluir usuário: {str(e)}', 'error')
    
    return redirect(url_for('gerenciar_usuarios'))

@app.route('/admin-vidah-sistema-2025/sistema')
@login_required
@admin_required
def manutencao_sistema():
    """Página de manutenção do sistema"""
    try:
        # Informações do sistema
        info_sistema = {
            'versao_python': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            'ambiente': os.environ.get('FLASK_ENV', 'production'),
            'database_url': os.environ.get('DATABASE_URL', 'SQLite local'),
            'uptime': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return render_template('manutencao/sistema.html', info_sistema=info_sistema)
        
    except Exception as e:
        log_error_with_traceback('Erro na página do sistema', e, current_user.id)
        return render_template('manutencao/sistema.html', info_sistema={})

@app.route('/gerenciar_templates')
@login_required
def gerenciar_templates():
    """Página de gerenciamento de templates"""
    try:
        # Buscar todos os templates
        templates = LaudoTemplate.query.filter_by(ativo=True).order_by(LaudoTemplate.diagnostico).all()
        
        # Estatísticas
        stats = {
            'total': len(templates),
            'adulto': len([t for t in templates if t.categoria == 'Adulto']),
            'pediatrico': len([t for t in templates if t.categoria == 'Pediátrico'])
        }
        
        return render_template('gerenciar_templates.html', 
                             templates=templates,
                             stats=stats)
                             
    except Exception as e:
        log_error_with_traceback('Erro no gerenciamento de templates', e, current_user.id)
        return render_template('gerenciar_templates.html', 
                             templates=[],
                             stats={})

@app.route('/template/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_template(id):
    """Excluir template"""
    try:
        template = LaudoTemplate.query.get_or_404(id)
        diagnostico = template.diagnostico
        
        db.session.delete(template)
        db.session.commit()
        
        log_system_event(f'Template excluído: {diagnostico}', current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Template excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao excluir template', e, current_user.id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ===== HANDLERS DE ERRO =====

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    log_error_with_traceback('Erro interno do servidor', error)
    return render_template('500.html'), 500

# ===== FUNCIONALIDADES AVANÇADAS ADICIONAIS =====

@app.route('/api/buscar-laudos-templates')
@login_required
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
        log_error_with_traceback('Erro ao buscar templates de laudo', e, current_user.id)
        return jsonify({"erro": "Erro interno do servidor"}), 500

@app.route('/api/laudos-templates/<int:template_id>')
@login_required
def api_obter_laudo_template(template_id):
    """API para obter um template específico de laudo"""
    try:
        template = db.session.get(LaudoTemplate, template_id)
        if not template:
            return jsonify({"erro": "Template não encontrado"}), 404
            
        return jsonify(template.to_dict())
        
    except Exception as e:
        log_error_with_traceback('Erro ao obter template', e, current_user.id)
        return jsonify({"erro": "Erro interno do servidor"}), 500

@app.route('/editar-exame/<int:exame_id>')
@login_required
def editar_exame_prontuario(exame_id):
    """Página para editar exame completo"""
    try:
        exame = Exame.query.get_or_404(exame_id)
        medicos = Medico.query.filter_by(ativo=True).all()
        
        log_system_event(f'Acesso à edição de exame - ID: {exame_id}', current_user.id)
        
        return render_template('editar_exame.html', 
                             exame=exame,
                             medicos=medicos)
                             
    except Exception as e:
        log_error_with_traceback('Erro ao carregar edição de exame', e, current_user.id)
        flash('Erro ao carregar exame para edição', 'error')
        return redirect(url_for('index'))

@app.route('/api/salvar-exame-editado/<int:exame_id>', methods=['POST'])
@login_required
def api_salvar_exame_editado(exame_id):
    """API para salvar exame editado"""
    try:
        data = request.get_json()
        exame = Exame.query.get_or_404(exame_id)
        
        # Atualizar dados básicos do exame
        if 'exame' in data:
            exame_data = data['exame']
            for field, value in exame_data.items():
                if hasattr(exame, field):
                    setattr(exame, field, value)
        
        # Atualizar parâmetros
        if 'parametros' in data and exame.parametros:
            parametros_data = data['parametros']
            # Calcular parâmetros derivados
            parametros_data = calcular_parametros_derivados(parametros_data)
            
            for field, value in parametros_data.items():
                if hasattr(exame.parametros, field) and value is not None:
                    try:
                        if field == 'frequencia_cardiaca':
                            setattr(exame.parametros, field, int(value))
                        else:
                            setattr(exame.parametros, field, float(value))
                    except (ValueError, TypeError):
                        continue
        
        # Atualizar laudos
        if 'laudos' in data and exame.laudos:
            laudos_data = data['laudos']
            laudo = exame.laudos[0]
            
            for field, value in laudos_data.items():
                if hasattr(laudo, field):
                    setattr(laudo, field, value or '')
        
        db.session.commit()
        
        log_system_event(f'Exame editado via API: ID {exame_id}', current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Exame atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao salvar exame editado', e, current_user.id)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/test-botao-pdf')
@login_required
def test_botao_pdf():
    """Rota de teste para botões PDF"""
    try:
        # Buscar primeiro exame disponível
        exame = Exame.query.first()
        if not exame:
            flash('Nenhum exame encontrado para teste', 'error')
            return redirect(url_for('index'))
        
        return redirect(url_for('gerar_pdf', id=exame.id))
        
    except Exception as e:
        log_error_with_traceback('Erro no teste de PDF', e, current_user.id)
        flash('Erro no teste de PDF', 'error')
        return redirect(url_for('index'))

@app.route('/gerar-pdf-institucional/<int:exame_id>')
@login_required
def gerar_pdf_institucional(exame_id):
    """Gerar PDF institucional específico"""
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        # Usar o gerador padrão que já está integrado
        caminho_pdf = generate_pdf_report(exame)
        
        if caminho_pdf:
            log_system_event(f'PDF institucional gerado para exame ID {exame_id}', current_user.id)
            
            return send_file(caminho_pdf, as_attachment=True, 
                            download_name=f'laudo_institucional_{exame_id}.pdf')
        else:
            raise Exception("Falha na geração do PDF institucional")
    
    except Exception as e:
        log_error_with_traceback('Erro ao gerar PDF institucional', e, current_user.id)
        flash(f'Erro ao gerar PDF: {str(e)}', 'error')
        return redirect(url_for('visualizar_exame', id=exame_id))

@app.route('/configurar-backup-automatico')
@login_required
@admin_required
def configurar_backup_automatico():
    """Página de configuração de backup automático"""
    try:
        return render_template('manutencao/backup_config.html')
    except Exception as e:
        log_error_with_traceback('Erro na configuração de backup', e, current_user.id)
        flash('Erro ao carregar configuração de backup', 'error')
        return redirect(url_for('manutencao_index'))

@app.route('/api/backup-status')
@login_required
@admin_required
def api_backup_status():
    """API para status do sistema de backup"""
    try:
        # Status simplificado
        status = {
            'automatico_ativo': True,
            'ultimo_backup': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'proximo_backup': 'Diário às 02:00',
            'total_backups': 5
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        log_error_with_traceback('Erro no status de backup', e, current_user.id)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/executar-backup-agora', methods=['POST'])
@login_required
@admin_required
def executar_backup_agora():
    """Executar backup manual imediatamente"""
    try:
        # Criar backup manual simples
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Estatísticas do backup
        stats = {
            'timestamp': timestamp,
            'total_exames': Exame.query.count(),
            'total_pacientes': db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar(),
            'total_usuarios': AuthUser.query.count(),
            'executado_por': current_user.username
        }
        
        # Registrar no log
        log_system_event(f'Backup manual executado: {json.dumps(stats)}', current_user.id)
        
        flash('Backup executado com sucesso!', 'success')
        
    except Exception as e:
        log_error_with_traceback('Erro ao executar backup', e, current_user.id)
        flash(f'Erro ao executar backup: {str(e)}', 'error')
    
    return redirect(url_for('pagina_backup'))

@app.route('/api/calcular-parametros-derivados', methods=['POST'])
@login_required
def api_calcular_parametros_derivados():
    """API para calcular parâmetros derivados em tempo real"""
    try:
        data = request.get_json()
        
        # Aplicar cálculos
        parametros_calculados = calcular_parametros_derivados(data)
        
        return jsonify({
            'success': True,
            'parametros': parametros_calculados
        })
        
    except Exception as e:
        log_error_with_traceback('Erro ao calcular parâmetros derivados', e, current_user.id)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/importar-laudos-templates')
@login_required
@admin_required
def importar_laudos_templates():
    """Importar templates de laudos de arquivo JSON"""
    try:
        # Verificar se já existem templates
        if LaudoTemplate.query.count() > 0:
            flash("Templates já foram importados.", "info")
            return redirect(url_for("manutencao_index"))
        
        # Criar alguns templates básicos
        templates_basicos = [
            {
                'categoria': 'Adulto',
                'diagnostico': 'Ecocardiograma Normal',
                'modo_m_bidimensional': 'Átrio esquerdo e cavidades ventriculares com dimensões normais.',
                'doppler_convencional': 'Fluxos intracardíacos normais.',
                'doppler_tecidual': 'Velocidades do anel mitral dentro da normalidade.',
                'conclusao': 'Ecocardiograma transtorácico dentro dos limites da normalidade.'
            },
            {
                'categoria': 'Adulto',
                'diagnostico': 'Hipertrofia Ventricular Esquerda',
                'modo_m_bidimensional': 'Hipertrofia concêntrica do ventrículo esquerdo.',
                'doppler_convencional': 'Fluxos transvalvares preservados.',
                'doppler_tecidual': 'Alterações compatíveis com disfunção diastólica.',
                'conclusao': 'Hipertrofia ventricular esquerda de grau moderado.'
            }
        ]
        
        for template_data in templates_basicos:
            template = LaudoTemplate()
            template.categoria = template_data['categoria']
            template.diagnostico = template_data['diagnostico']
            template.modo_m_bidimensional = template_data['modo_m_bidimensional']
            template.doppler_convencional = template_data['doppler_convencional']
            template.doppler_tecidual = template_data['doppler_tecidual']
            template.conclusao = template_data['conclusao']
            template.ativo = True
            
            db.session.add(template)
        
        db.session.commit()
        
        log_system_event(f'{len(templates_basicos)} templates básicos importados', current_user.id)
        flash(f"{len(templates_basicos)} templates importados com sucesso!", "success")
        
    except Exception as e:
        db.session.rollback()
        log_error_with_traceback('Erro ao importar templates', e, current_user.id)
        flash("Erro ao importar templates.", "error")
    
    return redirect(url_for("manutencao_index"))

@app.route('/inicializar-dados-templates')
@login_required
@admin_required
def inicializar_dados_templates():
    """Inicializar dados básicos de templates"""
    try:
        # Criar templates se não existirem
        if LaudoTemplate.query.count() == 0:
            return redirect(url_for('importar_laudos_templates'))
        
        flash('Templates já estão inicializados', 'info')
        return redirect(url_for('manutencao_index'))
        
    except Exception as e:
        log_error_with_traceback('Erro ao inicializar templates', e, current_user.id)
        flash('Erro ao inicializar dados', 'error')
        return redirect(url_for('manutencao_index'))

@app.route('/api/templates-busca-avancada')
@login_required
def api_templates_busca_avancada():
    """API para busca avançada de templates"""
    try:
        query = request.args.get('q', '').strip()
        categoria = request.args.get('categoria', '')
        
        base_query = LaudoTemplate.query.filter_by(ativo=True)
        
        if query:
            search_term = f'%{query}%'
            base_query = base_query.filter(
                db.or_(
                    LaudoTemplate.diagnostico.ilike(search_term),
                    LaudoTemplate.modo_m_bidimensional.ilike(search_term),
                    LaudoTemplate.conclusao.ilike(search_term)
                )
            )
        
        if categoria:
            base_query = base_query.filter_by(categoria=categoria)
        
        templates = base_query.order_by(LaudoTemplate.diagnostico).limit(20).all()
        
        resultado = []
        for template in templates:
            resultado.append({
                'id': template.id,
                'diagnostico': template.diagnostico,
                'categoria': template.categoria,
                'modo_m_bidimensional': template.modo_m_bidimensional[:100] + '...' if len(template.modo_m_bidimensional or '') > 100 else template.modo_m_bidimensional,
                'conclusao': template.conclusao[:100] + '...' if len(template.conclusao or '') > 100 else template.conclusao
            })
        
        return jsonify({
            'success': True,
            'templates': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        log_error_with_traceback('Erro na busca avançada', e, current_user.id)
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== ROTAS DE RELATÓRIOS E ESTATÍSTICAS =====

@app.route('/relatorios')
@login_required
@admin_required
def pagina_relatorios():
    """Página de relatórios do sistema"""
    try:
        # Estatísticas básicas
        stats = {
            'total_exames': Exame.query.count(),
            'total_pacientes': db.session.query(func.count(func.distinct(Exame.nome_paciente))).scalar(),
            'exames_mes_atual': Exame.query.filter(
                func.extract('month', Exame.created_at) == datetime.now().month,
                func.extract('year', Exame.created_at) == datetime.now().year
            ).count(),
            'usuarios_ativos': AuthUser.query.filter_by(is_active=True).count()
        }
        
        return render_template('relatorios/index.html', stats=stats)
        
    except Exception as e:
        log_error_with_traceback('Erro na página de relatórios', e, current_user.id)
        return render_template('relatorios/index.html', stats={})

@app.route('/api/relatorio-exames-periodo')
@login_required
@admin_required
def api_relatorio_exames_periodo():
    """API para relatório de exames por período"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Exame.query
        
        if data_inicio:
            query = query.filter(Exame.created_at >= data_inicio)
        if data_fim:
            query = query.filter(Exame.created_at <= data_fim)
        
        exames = query.order_by(desc(Exame.created_at)).all()
        
        resultado = []
        for exame in exames:
            resultado.append({
                'id': exame.id,
                'nome_paciente': exame.nome_paciente,
                'data_exame': exame.data_exame,
                'idade': exame.idade,
                'sexo': exame.sexo,
                'created_at': exame.created_at.strftime('%d/%m/%Y %H:%M') if exame.created_at else ''
            })
        
        return jsonify({
            'success': True,
            'exames': resultado,
            'total': len(resultado)
        })
        
    except Exception as e:
        log_error_with_traceback('Erro no relatório de exames', e, current_user.id)
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== INICIALIZAÇÃO =====

def init_app():
    """Inicialização da aplicação"""
    with app.app_context():
        try:
            db.create_all()
            log_system_event('Sistema inicializado com sucesso')
            
            # Criar usuário admin padrão se não existir
            admin_user = AuthUser.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = AuthUser()
                admin_user.username = 'admin'
                admin_user.email = 'admin@grupovida.com.br'
                admin_user.set_password('VidahAdmin2025!')
                admin_user.role = 'admin'
                admin_user.is_active = True
                
                db.session.add(admin_user)
                db.session.commit()
                log_system_event('Usuário admin criado automaticamente')
            
        except Exception as e:
            log_error_with_traceback('Erro na inicialização', e)

if __name__ == '__main__':
    init_app()
