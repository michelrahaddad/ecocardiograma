import os
import logging
from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import Usuario, Exame, ParametrosEcocardiograma, LaudoEcocardiograma, Medico, LogSistema, LaudoTemplate
from utils.pdf_generator_compacto import generate_pdf_report
from utils.calculations import calcular_superficie_corporal, calcular_volumes_teichholz, calcular_fracao_ejecao
import json
from werkzeug.utils import secure_filename

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_user_action(mensagem, nivel='INFO'):
    """Log de ações do usuário"""
    try:
        log = LogSistema(
            nivel=nivel,
            mensagem=mensagem,
            modulo='routes',
            usuario_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(log)
        db.session.commit()
        
        if nivel == 'INFO':
            logger.info(mensagem)
        elif nivel == 'WARNING':
            logger.warning(mensagem)
        elif nivel == 'ERROR':
            logger.error(mensagem)
    except Exception as e:
        logger.error(f"Erro ao registrar log: {str(e)}")

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except:
        return None

@app.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # CORREÇÃO: Usar Usuario ao invés de AuthUser
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password) and usuario.is_active():
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
    username = current_user.username
    logout_user()
    log_user_action(f'Logout realizado - Usuário {username}')
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth_login'))

@app.route('/')
@login_required
def index():
    try:
        total_exames = Exame.query.count()
        exames_recentes = Exame.query.order_by(Exame.created_at.desc()).limit(5).all()
        
        return render_template('index.html', 
                             total_exames=total_exames,
                             exames_recentes=exames_recentes)
    except Exception as e:
        logger.error(f"Erro na página inicial: {str(e)}")
        flash('Erro ao carregar dados da página inicial.', 'error')
        return render_template('index.html', total_exames=0, exames_recentes=[])

@app.route('/novo_exame', methods=['GET', 'POST'])
@login_required
def novo_exame():
    if request.method == 'POST':
        try:
            # Dados do exame
            nome_paciente = request.form['nome_paciente']
            data_nascimento = request.form['data_nascimento']
            idade = int(request.form['idade'])
            sexo = request.form['sexo']
            data_exame = request.form['data_exame']
            tipo_atendimento = request.form.get('tipo_atendimento', '')
            medico_usuario = request.form.get('medico_usuario', '')
            medico_solicitante = request.form.get('medico_solicitante', '')
            indicacao = request.form.get('indicacao', '')
            
            # Criar novo exame
            exame = Exame(
                nome_paciente=nome_paciente,
                data_nascimento=data_nascimento,
                idade=idade,
                sexo=sexo,
                data_exame=data_exame,
                tipo_atendimento=tipo_atendimento,
                medico_usuario=medico_usuario,
                medico_solicitante=medico_solicitante,
                indicacao=indicacao
            )
            
            db.session.add(exame)
            db.session.flush()  # Para obter o ID
            
            # Criar parâmetros padrão
            parametros = ParametrosEcocardiograma(exame_id=exame.id)
            db.session.add(parametros)
            
            # Criar laudo padrão
            laudo = LaudoEcocardiograma(exame_id=exame.id)
            db.session.add(laudo)
            
            db.session.commit()
            
            log_user_action(f'Novo exame criado - ID: {exame.id}, Paciente: {nome_paciente}')
            flash('Exame criado com sucesso!', 'success')
            
            return redirect(url_for('parametros', exame_id=exame.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar exame: {str(e)}")
            flash('Erro ao criar exame. Tente novamente.', 'error')
    
    # Verificar se há parâmetros para clonar
    clone_paciente = request.args.get('clone_paciente')
    dados_clonados = {}
    
    if clone_paciente:
        try:
            # Buscar último exame do paciente
            ultimo_exame = Exame.query.filter_by(nome_paciente=clone_paciente).order_by(Exame.created_at.desc()).first()
            if ultimo_exame and ultimo_exame.parametros:
                dados_clonados = {
                    'nome_paciente': ultimo_exame.nome_paciente,
                    'data_nascimento': ultimo_exame.data_nascimento,
                    'idade': ultimo_exame.idade,
                    'sexo': ultimo_exame.sexo,
                    'tipo_atendimento': ultimo_exame.tipo_atendimento,
                    'medico_usuario': ultimo_exame.medico_usuario,
                    'medico_solicitante': ultimo_exame.medico_solicitante,
                    'indicacao': ultimo_exame.indicacao,
                    'parametros': ultimo_exame.parametros,
                    'laudos': ultimo_exame.laudos[0] if ultimo_exame.laudos else None
                }
        except Exception as e:
            logger.error(f"Erro ao clonar dados: {str(e)}")
    
    return render_template('novo_exame.html', dados_clonados=dados_clonados)

@app.route('/parametros/<int:exame_id>')
@login_required
def parametros(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        if not exame.parametros:
            parametros = ParametrosEcocardiograma(exame_id=exame_id)
            db.session.add(parametros)
            db.session.commit()
        
        return render_template('parametros.html', exame=exame)
    except Exception as e:
        logger.error(f"Erro ao carregar parâmetros: {str(e)}")
        flash('Erro ao carregar parâmetros do exame.', 'error')
        return redirect(url_for('index'))

@app.route('/salvar_parametros/<int:exame_id>', methods=['POST'])
@login_required
def salvar_parametros(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        if not exame.parametros:
            parametros = ParametrosEcocardiograma(exame_id=exame_id)
            db.session.add(parametros)
        else:
            parametros = exame.parametros
        
        # Atualizar parâmetros com dados do formulário
        for field_name in request.form:
            if hasattr(parametros, field_name):
                value = request.form[field_name]
                if value:
                    try:
                        setattr(parametros, field_name, float(value))
                    except ValueError:
                        setattr(parametros, field_name, value)
        
        db.session.commit()
        log_user_action(f'Parâmetros salvos - Exame ID: {exame_id}')
        flash('Parâmetros salvos com sucesso!', 'success')
        
        return redirect(url_for('laudo', exame_id=exame_id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar parâmetros: {str(e)}")
        flash('Erro ao salvar parâmetros.', 'error')
        return redirect(url_for('parametros', exame_id=exame_id))

@app.route('/laudo/<int:exame_id>')
@login_required
def laudo(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        if not exame.laudos:
            laudo = LaudoEcocardiograma(exame_id=exame_id)
            db.session.add(laudo)
            db.session.commit()
        
        return render_template('laudo.html', exame=exame)
    except Exception as e:
        logger.error(f"Erro ao carregar laudo: {str(e)}")
        flash('Erro ao carregar laudo do exame.', 'error')
        return redirect(url_for('index'))

@app.route('/salvar_laudo/<int:exame_id>', methods=['POST'])
@login_required
def salvar_laudo(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        if exame.laudos:
            laudo = exame.laudos[0]
        else:
            laudo = LaudoEcocardiograma(exame_id=exame_id)
            db.session.add(laudo)
        
        # Atualizar campos do laudo
        laudo.modo_m_bidimensional = request.form.get('modo_m_bidimensional', '')
        laudo.doppler_convencional = request.form.get('doppler_convencional', '')
        laudo.doppler_tecidual = request.form.get('doppler_tecidual', '')
        laudo.conclusao = request.form.get('conclusao', '')
        laudo.recomendacoes = request.form.get('recomendacoes', '')
        
        db.session.commit()
        log_user_action(f'Laudo salvo - Exame ID: {exame_id}')
        flash('Laudo salvo com sucesso!', 'success')
        
        return redirect(url_for('laudo', exame_id=exame_id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar laudo: {str(e)}")
        flash('Erro ao salvar laudo.', 'error')
        return redirect(url_for('laudo', exame_id=exame_id))

@app.route('/gerar-pdf/<int:exame_id>')
@login_required
def gerar_pdf(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        
        # Gerar PDF
        pdf_path = generate_pdf_report(exame)
        
        log_user_action(f'PDF gerado - Exame ID: {exame_id}')
        
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f'laudo_ecocardiograma_{exame.nome_paciente}_{exame.data_exame}.pdf')
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        flash('Erro ao gerar PDF.', 'error')
        return redirect(url_for('laudo', exame_id=exame_id))

@app.route('/prontuario')
@login_required
def prontuario():
    return render_template('prontuario/busca.html')

@app.route('/buscar-pacientes')
@login_required
def buscar_pacientes():
    try:
        termo = request.args.get('termo', '').strip()
        
        if not termo:
            return jsonify([])
        
        # Busca por nome do paciente
        exames = Exame.query.filter(
            Exame.nome_paciente.ilike(f'%{termo}%')
        ).order_by(Exame.created_at.desc()).limit(50).all()
        
        # Agrupar por paciente
        pacientes = {}
        for exame in exames:
            nome = exame.nome_paciente
            if nome not in pacientes:
                pacientes[nome] = {
                    'nome': nome,
                    'ultimo_exame': exame.data_exame,
                    'total_exames': 0,
                    'id_ultimo_exame': exame.id
                }
            pacientes[nome]['total_exames'] += 1
        
        return jsonify(list(pacientes.values()))
    except Exception as e:
        logger.error(f"Erro na busca de pacientes: {str(e)}")
        return jsonify([])

@app.route('/prontuario/paciente/<nome_paciente>')
@login_required
def prontuario_paciente(nome_paciente):
    try:
        exames = Exame.query.filter_by(nome_paciente=nome_paciente).order_by(Exame.created_at.desc()).all()
        
        if not exames:
            flash('Paciente não encontrado.', 'error')
            return redirect(url_for('prontuario'))
        
        return render_template('prontuario/paciente.html', 
                             exames=exames, 
                             nome_paciente=nome_paciente)
    except Exception as e:
        logger.error(f"Erro ao carregar prontuário: {str(e)}")
        flash('Erro ao carregar prontuário do paciente.', 'error')
        return redirect(url_for('prontuario'))

@app.route('/visualizar_exame/<int:exame_id>')
@login_required
def visualizar_exame(exame_id):
    try:
        exame = Exame.query.get_or_404(exame_id)
        return render_template('visualizar_exame.html', exame=exame)
    except Exception as e:
        logger.error(f"Erro ao visualizar exame: {str(e)}")
        flash('Erro ao carregar exame.', 'error')
        return redirect(url_for('index'))

@app.route('/inicializar_sistema')
def inicializar_sistema():
    try:
        # Verificar se já existem usuários
        if Usuario.query.count() > 0:
            flash('Sistema já inicializado.', 'info')
            return redirect(url_for('auth_login'))
        
        # Criar usuário administrador padrão
        admin = Usuario(
            username='admin',
            email='admin@grupovidah.com.br',
            role='admin',
            ativo=True
        )
        admin.set_password('VidahAdmin2025!')
        
        # Criar usuário comum
        usuario = Usuario(
            username='usuario',
            email='usuario@grupovidah.com.br',
            role='user',
            ativo=True
        )
        usuario.set_password('Usuario123!')
        
        db.session.add(admin)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Sistema inicializado com sucesso! Use admin/VidahAdmin2025! ou usuario/Usuario123!', 'success')
        return redirect(url_for('auth_login'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao inicializar sistema: {str(e)}")
        flash('Erro ao inicializar sistema.', 'error')
        return redirect(url_for('auth_login'))

# APIs para cálculos automáticos
@app.route('/api/calcular-superficie', methods=['POST'])
@login_required
def api_calcular_superficie():
    try:
        data = request.get_json()
        peso = float(data.get('peso', 0))
        altura = float(data.get('altura', 0))
        
        superficie = calcular_superficie_corporal(peso, altura)
        return jsonify({'superficie_corporal': round(superficie, 2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/calcular-volumes', methods=['POST'])
@login_required
def api_calcular_volumes():
    try:
        data = request.get_json()
        ddve = float(data.get('ddve', 0))
        dsve = float(data.get('dsve', 0))
        
        volumes = calcular_volumes_teichholz(ddve, dsve)
        return jsonify(volumes)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False)
