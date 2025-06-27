"""
Routes Modulares - Sistema de Ecocardiograma

Blueprints organizados por funcionalidade, eliminando código duplicado
e implementando padrões anti-bug.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Blueprint Principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Página inicial com estatísticas e exames recentes"""
    try:
        # Importar módulos de forma simples para evitar problemas de circular import
        from models import Exame
        from app_new import db
        
        # Buscar exames recentes diretamente do banco
        recent_exams = db.session.query(Exame).order_by(Exame.created_at.desc()).limit(10).all()
        
        # Estatísticas básicas
        total_exames = db.session.query(Exame).count()
        exames_hoje = db.session.query(Exame).filter(
            db.func.date(Exame.created_at) == db.func.current_date()
        ).count()
        
        stats = {
            'total_exames': total_exames,
            'exames_hoje': exames_hoje,
            'total_medicos': 0,
            'parametros_preenchidos': 0
        }
        
        return render_template('index.html', 
                             exames=recent_exams,
                             stats=stats)
    except Exception as e:
        logger.error(f"Erro na página inicial: {e}")
        flash("Erro ao carregar dados da página inicial", "error")
        return render_template('index.html', exames=[], stats={})

# Blueprint de Exames
exams_bp = Blueprint('exams', __name__)

@exams_bp.route('/novo', methods=['GET', 'POST'])
def novo_exame():
    """Criar novo exame"""
    if request.method == 'POST':
        try:
            from models import Exame
            from app_new import db
            from datetime import datetime
            
            # Calcular idade
            data_nasc = request.form.get('data_nascimento')
            if data_nasc:
                birth_date = datetime.strptime(data_nasc, '%d/%m/%Y')
                age = datetime.now().year - birth_date.year
                if datetime.now().month < birth_date.month or (datetime.now().month == birth_date.month and datetime.now().day < birth_date.day):
                    age -= 1
            else:
                age = 0
            
            # Criar exame
            exam = Exame()
            exam.nome_paciente = request.form.get('nome_paciente')
            exam.data_nascimento = request.form.get('data_nascimento')
            exam.idade = age
            exam.sexo = request.form.get('sexo')
            exam.data_exame = request.form.get('data_exame')
            exam.tipo_atendimento = request.form.get('tipo_atendimento', '')
            exam.medico_usuario = request.form.get('medico_usuario', '')
            exam.medico_solicitante = request.form.get('medico_solicitante', '')
            exam.indicacao = request.form.get('indicacao', '')
            
            db.session.add(exam)
            db.session.commit()
            
            flash("Exame criado com sucesso!", "success")
            return redirect(url_for('exams.parametros', exame_id=exam.id))
            
        except Exception as e:
            logger.error(f"Erro ao criar exame: {e}")
            flash(f"Erro ao criar exame: {str(e)}", "error")
            db.session.rollback()
    
    return render_template('novo_exame.html')

@exams_bp.route('/<int:exame_id>/parametros', methods=['GET', 'POST'])
def parametros(exame_id):
    """Formulário de parâmetros do ecocardiograma"""
    try:
        from modules.exams.exam_service import ExamService
        from modules.exams.parameter_service import ParameterService
        
        exam = ExamService.get_exam(exame_id)
        if not exam:
            flash("Exame não encontrado", "error")
            return redirect(url_for('main.index'))
        
        if request.method == 'POST':
            try:
                # Obter todos os dados do formulário
                param_data = {}
                for key, value in request.form.items():
                    if value and value.strip():
                        param_data[key] = value.strip()
                
                # Salvar parâmetros
                ParameterService.save_parameters(exame_id, param_data)
                flash("Parâmetros salvos com sucesso!", "success")
                return redirect(url_for('exams.laudo', exame_id=exame_id))
                
            except Exception as e:
                logger.error(f"Erro ao salvar parâmetros: {e}")
                flash(f"Erro ao salvar parâmetros: {str(e)}", "error")
        
        # Buscar parâmetros existentes
        existing_params = ParameterService.get_parameters(exame_id)
        
        return render_template('parametros.html', 
                             exame=exam, 
                             parametros=existing_params)
                             
    except Exception as e:
        logger.error(f"Erro na página de parâmetros: {e}")
        flash("Erro ao carregar página de parâmetros", "error")
        return redirect(url_for('main.index'))

@exams_bp.route('/<int:exame_id>/laudo', methods=['GET', 'POST'])
def laudo(exame_id):
    """Formulário de laudo do ecocardiograma"""
    try:
        from modules.exams.exam_service import ExamService
        from modules.reports.laudo_service import LaudoService
        
        exam = ExamService.get_exam(exame_id)
        if not exam:
            flash("Exame não encontrado", "error")
            return redirect(url_for('main.index'))
        
        if request.method == 'POST':
            try:
                laudo_data = {
                    'modo_m_bidimensional': request.form.get('modo_m_bidimensional', ''),
                    'doppler_convencional': request.form.get('doppler_convencional', ''),
                    'doppler_tecidual': request.form.get('doppler_tecidual', ''),
                    'conclusao': request.form.get('conclusao', ''),
                    'recomendacoes': request.form.get('recomendacoes', '')
                }
                
                LaudoService.save_laudo(exame_id, laudo_data)
                flash("Laudo salvo com sucesso!", "success")
                return redirect(url_for('exams.visualizar', exame_id=exame_id))
                
            except Exception as e:
                logger.error(f"Erro ao salvar laudo: {e}")
                flash(f"Erro ao salvar laudo: {str(e)}", "error")
        
        # Buscar laudo existente
        existing_laudo = LaudoService.get_laudo(exame_id)
        
        return render_template('laudo.html', 
                             exame=exam, 
                             laudo=existing_laudo)
                             
    except Exception as e:
        logger.error(f"Erro na página de laudo: {e}")
        flash("Erro ao carregar página de laudo", "error")
        return redirect(url_for('main.index'))

@exams_bp.route('/<int:exame_id>/visualizar')
def visualizar(exame_id):
    """Visualização completa do exame"""
    try:
        from modules.exams.exam_service import ExamService
        from modules.exams.parameter_service import ParameterService
        from modules.reports.laudo_service import LaudoService
        
        exam = ExamService.get_exam(exame_id)
        if not exam:
            flash("Exame não encontrado", "error")
            return redirect(url_for('main.index'))
        
        parameters = ParameterService.get_parameters(exame_id)
        laudo = LaudoService.get_laudo(exame_id)
        
        return render_template('visualizar_exame.html',
                             exame=exam,
                             parametros=parameters,
                             laudo=laudo)
                             
    except Exception as e:
        logger.error(f"Erro ao visualizar exame: {e}")
        flash("Erro ao carregar exame", "error")
        return redirect(url_for('main.index'))

@exams_bp.route('/<int:exame_id>/deletar', methods=['POST'])
def deletar(exame_id):
    """Deletar exame"""
    try:
        from modules.exams.exam_service import ExamService
        
        if ExamService.delete_exam(exame_id):
            flash("Exame excluído com sucesso!", "success")
        else:
            flash("Erro ao excluir exame", "error")
            
    except Exception as e:
        logger.error(f"Erro ao deletar exame: {e}")
        flash(f"Erro ao excluir exame: {str(e)}", "error")
    
    return redirect(url_for('main.index'))

@exams_bp.route('/paciente/<nome_paciente>')
def exames_paciente(nome_paciente):
    """Lista exames de um paciente específico"""
    try:
        from modules.exams.exam_service import ExamService
        
        exams = ExamService.get_patient_exams(nome_paciente)
        
        return render_template('exames_paciente.html',
                             nome_paciente=nome_paciente,
                             exames=exams)
                             
    except Exception as e:
        logger.error(f"Erro ao buscar exames do paciente: {e}")
        flash("Erro ao carregar exames do paciente", "error")
        return redirect(url_for('main.index'))

# Blueprint de Relatórios
reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/<int:exame_id>/pdf')
def gerar_pdf(exame_id):
    """Gerar PDF do exame"""
    try:
        from modules.reports.pdf_service import PDFService
        
        pdf_response = PDFService.generate_exam_pdf(exame_id)
        return pdf_response
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        flash(f"Erro ao gerar PDF: {str(e)}", "error")
        return redirect(url_for('exams.visualizar', exame_id=exame_id))

# Blueprint de Manutenção
maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/')
def index():
    """Painel principal de manutenção"""
    try:
        from modules.maintenance.system_service import SystemService
        
        system_status = SystemService.get_system_status()
        
        return render_template('manutencao/index.html',
                             status=system_status)
                             
    except Exception as e:
        logger.error(f"Erro no painel de manutenção: {e}")
        flash("Erro ao carregar painel de manutenção", "error")
        return render_template('manutencao/index.html', status={})

@maintenance_bp.route('/backup')
def backup():
    """Página de backup e restauração"""
    return render_template('manutencao/backup.html')

@maintenance_bp.route('/logs')
def logs():
    """Página de visualização de logs"""
    return render_template('manutencao/logs.html')

# API Routes para AJAX
@main_bp.route('/api/medicos')
def api_medicos():
    """API para obter lista de médicos"""
    try:
        from models import Medico
        medicos = Medico.query.filter_by(ativo=True).all()
        return jsonify([{
            'id': m.id,
            'nome': m.nome,
            'crm': m.crm
        } for m in medicos])
    except Exception as e:
        logger.error(f"Erro na API de médicos: {e}")
        return jsonify([])

@main_bp.route('/api/calculos', methods=['POST'])
def api_calculos():
    """API para cálculos em tempo real"""
    try:
        from modules.exams.parameter_service import ParameterService
        
        param_data = request.get_json()
        calculated_values = ParameterService.calculate_derived_values(param_data)
        
        return jsonify(calculated_values)
        
    except Exception as e:
        logger.error(f"Erro nos cálculos: {e}")
        return jsonify({'error': str(e)}), 400