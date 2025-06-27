import sqlite3
import os
import json
import weasyprint
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from integracao_modelos import integrar_modelos_laudo
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'vidah_ecocardiograma_2025'

# Integrar modelos de laudo
diretorio_base = os.path.dirname(os.path.abspath(__file__))
integrador_modelos = integrar_modelos_laudo(app, os.path.dirname(diretorio_base))

# Configuração do banco de dados
DATABASE = 'ecocardiograma.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Criar tabela de exames
    conn.execute('''
    CREATE TABLE IF NOT EXISTS exames (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT NOT NULL,
        data_nascimento TEXT,
        idade TEXT,
        sexo TEXT,
        data_exame TEXT,
        medico_solicitante TEXT,
        medico_usuario TEXT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Criar tabela de parâmetros
    conn.execute('''
    CREATE TABLE IF NOT EXISTS parametros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exame_id INTEGER,
        peso TEXT,
        altura TEXT,
        superficie_corporal TEXT,
        frequencia_cardiaca TEXT,
        atrio_esquerdo TEXT,
        raiz_aorta TEXT,
        relacao_atrio_esquerdo_aorta TEXT,
        aorta_ascendente TEXT,
        diametro_ventricular_direito TEXT,
        diametro_basal_vd TEXT,
        diametro_diastolico_final_ve TEXT,
        diametro_sistolico_final TEXT,
        percentual_encurtamento TEXT,
        espessura_diastolica_septo TEXT,
        espessura_diastolica_ppve TEXT,
        relacao_septo_parede_posterior TEXT,
        volume_diastolico_final TEXT,
        volume_sistolico_final TEXT,
        volume_sistolico TEXT,
        fracao_ejecao_teichols TEXT,
        fracao_ejecao_simpson TEXT,
        fracao_ejecao TEXT,
        debito_cardiaco TEXT,
        indice_cardiaco TEXT,
        volume_atrio_esquerdo TEXT,
        massa_ve TEXT,
        indice_massa_ve TEXT,
        relacao_volume_massa TEXT,
        fluxo_pulmonar TEXT,
        gradiente_vd_ap TEXT,
        fluxo_aortico TEXT,
        gradiente_ve_ao TEXT,
        fluxo_mitral TEXT,
        gradiente_ae_ve TEXT,
        fluxo_tricuspide TEXT,
        gradiente_ad_vd TEXT,
        pressao_atrio_direito TEXT,
        psap TEXT,
        FOREIGN KEY (exame_id) REFERENCES exames (id)
    )
    ''')
    
    # Criar tabela de laudos
    conn.execute('''
    CREATE TABLE IF NOT EXISTS laudos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exame_id INTEGER,
        resumo_exame TEXT,
        medico_responsavel TEXT,
        crm_medico TEXT,
        ritmo_cardiaco TEXT,
        ventriculo_esquerdo TEXT,
        ventriculo_direito TEXT,
        valvas TEXT,
        pericardio TEXT,
        aorta TEXT,
        achados_ecocardiograficos TEXT,
        conclusao TEXT,
        observacoes TEXT,
        signature_data TEXT,
        FOREIGN KEY (exame_id) REFERENCES exames (id)
    )
    ''')
    
    # Criar tabela de modelos de laudo
    conn.execute('''
    CREATE TABLE IF NOT EXISTS modelos_laudo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        conteudo TEXT NOT NULL
    )
    ''')
    
    # Criar tabela de médicos
    conn.execute('''
    CREATE TABLE IF NOT EXISTS medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        crm TEXT NOT NULL,
        assinatura_data TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Inicializar banco de dados
if not os.path.exists(DATABASE):
    init_db()
else:
    # Verificar se a tabela médicos existe
    conn = get_db_connection()
    try:
        conn.execute('SELECT * FROM medicos LIMIT 1')
    except sqlite3.OperationalError:
        # Se a tabela não existir, criar
        conn.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT NOT NULL,
            assinatura_data TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    conn.close()
    
# Carregar modelos de laudo
conn = get_db_connection()

# Verificar se já existem modelos
modelos_count = conn.execute('SELECT COUNT(*) FROM modelos_laudo').fetchone()[0]

if modelos_count == 0:
    # Carregar modelos de arquivos de texto
    modelos_dir = os.path.join(os.path.dirname(__file__), 'modelos_laudo')
    
    if os.path.exists(modelos_dir):
        for filename in os.listdir(modelos_dir):
            if filename.endswith('.txt'):
                nome_modelo = os.path.splitext(filename)[0]
                
                try:
                    with open(os.path.join(modelos_dir, filename), 'r', encoding='utf-8') as file:
                        conteudo = file.read()
                        
                        conn.execute('INSERT INTO modelos_laudo (nome, conteudo) VALUES (?, ?)',
                                    (nome_modelo, conteudo))
                except Exception as e:
                    print(f"Erro ao carregar modelo {filename}: {e}")
        
        conn.commit()

# Cadastrar médico padrão se não existir
try:
    medicos_count = conn.execute('SELECT COUNT(*) FROM medicos').fetchone()[0]
    
    if medicos_count == 0:
        conn.execute('''
        INSERT INTO medicos (nome, crm, assinatura_data)
        VALUES (?, ?, ?)
        ''', ('Michel Raineri Haddad', '183299', ''))
        conn.commit()
except Exception as e:
    print(f"Erro ao verificar médicos: {e}")

conn.close()

# Rotas da aplicação
@app.route('/')
def index():
    conn = get_db_connection()
    # Buscar todos os exames, mas agrupar por nome de paciente para a exibição inicial
    exames = conn.execute('SELECT * FROM exames ORDER BY data_criacao DESC').fetchall()
    
    # Criar um dicionário para armazenar o exame mais recente de cada paciente
    pacientes_unicos = {}
    for exame in exames:
        nome_paciente = exame['nome_paciente']
        if nome_paciente not in pacientes_unicos:
            pacientes_unicos[nome_paciente] = exame
    
    # Converter o dicionário de volta para uma lista
    exames_unicos = list(pacientes_unicos.values())
    
    conn.close()
    return render_template('index.html', exames=exames_unicos, todos_exames=exames)

@app.route('/exames_paciente/<nome_paciente>')
def exames_paciente(nome_paciente):
    conn = get_db_connection()
    exames = conn.execute('SELECT * FROM exames WHERE nome_paciente = ? ORDER BY data_exame DESC', 
                         (nome_paciente,)).fetchall()
    conn.close()
    
    if not exames:
        flash('Nenhum exame encontrado para este paciente.', 'error')
        return redirect(url_for('index'))
    
    return render_template('exames_paciente.html', exames=exames, nome_paciente=nome_paciente)

@app.route('/novo_exame', methods=['GET', 'POST'])
def novo_exame():
    if request.method == 'POST':
        nome_paciente = request.form['nome_paciente']
        data_nascimento = request.form['data_nascimento']
        idade = request.form['idade']
        sexo = request.form['sexo']
        data_exame = request.form['data_exame']
        medico_solicitante = request.form['medico_solicitante']
        medico_usuario = request.form['medico_usuario']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO exames (nome_paciente, data_nascimento, idade, sexo, data_exame, medico_solicitante, medico_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome_paciente, data_nascimento, idade, sexo, data_exame, medico_solicitante, medico_usuario))
        
        exame_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash('Exame criado com sucesso!', 'success')
        return redirect(url_for('parametros', exame_id=exame_id))
    
    return render_template('formulario_exame.html')

# Rota para visualizar exame
@app.route('/visualizar_exame/<int:exame_id>')
def visualizar_exame(exame_id):
    conn = get_db_connection()
    exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
    
    if exame is None:
        conn.close()
        flash('Exame não encontrado!', 'error')
        return redirect(url_for('index'))
    
    parametros = conn.execute('SELECT * FROM parametros WHERE exame_id = ?', (exame_id,)).fetchone()
    laudo = conn.execute('SELECT * FROM laudos WHERE exame_id = ?', (exame_id,)).fetchone()
    conn.close()
    
    return render_template('visualizar_exame.html', exame=exame, parametros=parametros, laudo=laudo)

@app.route('/exame/<int:exame_id>/parametros', methods=['GET', 'POST'])
def parametros(exame_id):
    conn = get_db_connection()
    exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
    
    if exame is None:
        conn.close()
        flash('Exame não encontrado!', 'error')
        return redirect(url_for('index'))
    
    parametros = conn.execute('SELECT * FROM parametros WHERE exame_id = ?', (exame_id,)).fetchone()
    conn.close()
    
    return render_template('parametros_ecocardiograma.html', exame=exame, parametros=parametros)

@app.route('/exame/<int:exame_id>/salvar_parametros', methods=['POST'])
def salvar_parametros(exame_id):
    if request.method == 'POST':
        # Usar get() para todos os campos para evitar KeyError
        peso = request.form.get('peso', '')
        altura = request.form.get('altura', '')
        superficie_corporal = request.form.get('superficie_corporal', '')
        frequencia_cardiaca = request.form.get('frequencia_cardiaca', '')
        atrio_esquerdo = request.form.get('atrio_esquerdo', '')
        raiz_aorta = request.form.get('raiz_aorta', '')
        relacao_atrio_esquerdo_aorta = request.form.get('relacao_atrio_esquerdo_aorta', '')
        aorta_ascendente = request.form.get('aorta_ascendente', '')
        diametro_ventricular_direito = request.form.get('diametro_ventricular_direito', '')
        diametro_basal_vd = request.form.get('diametro_basal_vd', '')
        diametro_diastolico_final_ve = request.form.get('diametro_diastolico_final_ve', '')
        diametro_sistolico_final = request.form.get('diametro_sistolico_final', '')
        percentual_encurtamento = request.form.get('percentual_encurtamento', '')
        espessura_diastolica_septo = request.form.get('espessura_diastolica_septo', '')
        espessura_diastolica_ppve = request.form.get('espessura_diastolica_ppve', '')
        relacao_septo_parede_posterior = request.form.get('relacao_septo_parede_posterior', '')
        volume_diastolico_final = request.form.get('volume_diastolico_final', '')
        volume_sistolico_final = request.form.get('volume_sistolico_final', '')
        volume_sistolico = request.form.get('volume_sistolico', '')
        fracao_ejecao_teichols = request.form.get('fracao_ejecao_teichols', '')
        fracao_ejecao_simpson = request.form.get('fracao_ejecao_simpson', '')
        fracao_ejecao = request.form.get('fracao_ejecao', '')
        debito_cardiaco = request.form.get('debito_cardiaco', '')
        indice_cardiaco = request.form.get('indice_cardiaco', '')
        volume_atrio_esquerdo = request.form.get('volume_atrio_esquerdo', '')
        massa_ve = request.form.get('massa_ve', '')
        indice_massa_ve = request.form.get('indice_massa_ve', '')
        relacao_volume_massa = request.form.get('relacao_volume_massa', '')
        fluxo_pulmonar = request.form.get('fluxo_pulmonar', '')
        gradiente_vd_ap = request.form.get('gradiente_vd_ap', '')
        fluxo_aortico = request.form.get('fluxo_aortico', '')
        gradiente_ve_ao = request.form.get('gradiente_ve_ao', '')
        fluxo_mitral = request.form.get('fluxo_mitral', '')
        gradiente_ae_ve = request.form.get('gradiente_ae_ve', '')
        fluxo_tricuspide = request.form.get('fluxo_tricuspide', '')
        gradiente_ad_vd = request.form.get('gradiente_ad_vd', '')
        pressao_atrio_direito = request.form.get('pressao_atrio_direito', '')
        psap = request.form.get('psap', '')
        
        conn = get_db_connection()
        exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
        
        if exame is None:
            conn.close()
            flash('Exame não encontrado!', 'error')
            return redirect(url_for('index'))
        
        parametros = conn.execute('SELECT * FROM parametros WHERE exame_id = ?', (exame_id,)).fetchone()
        
        if parametros:
            # Atualizar parâmetros existentes
            conn.execute('''
            UPDATE parametros SET 
                peso = ?,
                altura = ?,
                superficie_corporal = ?,
                frequencia_cardiaca = ?,
                atrio_esquerdo = ?,
                raiz_aorta = ?,
                relacao_atrio_esquerdo_aorta = ?,
                aorta_ascendente = ?,
                diametro_ventricular_direito = ?,
                diametro_basal_vd = ?,
                diametro_diastolico_final_ve = ?,
                diametro_sistolico_final = ?,
                percentual_encurtamento = ?,
                espessura_diastolica_septo = ?,
                espessura_diastolica_ppve = ?,
                relacao_septo_parede_posterior = ?,
                volume_diastolico_final = ?,
                volume_sistolico_final = ?,
                volume_sistolico = ?,
                fracao_ejecao_teichols = ?,
                fracao_ejecao_simpson = ?,
                fracao_ejecao = ?,
                debito_cardiaco = ?,
                indice_cardiaco = ?,
                volume_atrio_esquerdo = ?,
                massa_ve = ?,
                indice_massa_ve = ?,
                relacao_volume_massa = ?,
                fluxo_pulmonar = ?,
                gradiente_vd_ap = ?,
                fluxo_aortico = ?,
                gradiente_ve_ao = ?,
                fluxo_mitral = ?,
                gradiente_ae_ve = ?,
                fluxo_tricuspide = ?,
                gradiente_ad_vd = ?,
                pressao_atrio_direito = ?,
                psap = ?
            WHERE exame_id = ?
            ''', (peso, altura, superficie_corporal, frequencia_cardiaca, atrio_esquerdo, raiz_aorta, 
                  relacao_atrio_esquerdo_aorta, aorta_ascendente, diametro_ventricular_direito, 
                  diametro_basal_vd, diametro_diastolico_final_ve, diametro_sistolico_final, 
                  percentual_encurtamento, espessura_diastolica_septo, espessura_diastolica_ppve, 
                  relacao_septo_parede_posterior, volume_diastolico_final, volume_sistolico_final, 
                  volume_sistolico, fracao_ejecao_teichols, fracao_ejecao_simpson, fracao_ejecao, 
                  debito_cardiaco, indice_cardiaco, volume_atrio_esquerdo, massa_ve, indice_massa_ve, 
                  relacao_volume_massa, fluxo_pulmonar, gradiente_vd_ap, fluxo_aortico, gradiente_ve_ao, 
                  fluxo_mitral, gradiente_ae_ve, fluxo_tricuspide, gradiente_ad_vd, pressao_atrio_direito, 
                  psap, exame_id))
        else:
            # Inserir novos parâmetros
            conn.execute('''
            INSERT INTO parametros (
                exame_id, peso, altura, superficie_corporal, frequencia_cardiaca, atrio_esquerdo, 
                raiz_aorta, relacao_atrio_esquerdo_aorta, aorta_ascendente, diametro_ventricular_direito, 
                diametro_basal_vd, diametro_diastolico_final_ve, diametro_sistolico_final, 
                percentual_encurtamento, espessura_diastolica_septo, espessura_diastolica_ppve, 
                relacao_septo_parede_posterior, volume_diastolico_final, volume_sistolico_final, 
                volume_sistolico, fracao_ejecao_teichols, fracao_ejecao_simpson, fracao_ejecao, 
                debito_cardiaco, indice_cardiaco, volume_atrio_esquerdo, massa_ve, indice_massa_ve, 
                relacao_volume_massa, fluxo_pulmonar, gradiente_vd_ap, fluxo_aortico, gradiente_ve_ao, 
                fluxo_mitral, gradiente_ae_ve, fluxo_tricuspide, gradiente_ad_vd, pressao_atrio_direito, psap
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (exame_id, peso, altura, superficie_corporal, frequencia_cardiaca, atrio_esquerdo, 
                  raiz_aorta, relacao_atrio_esquerdo_aorta, aorta_ascendente, diametro_ventricular_direito, 
                  diametro_basal_vd, diametro_diastolico_final_ve, diametro_sistolico_final, 
                  percentual_encurtamento, espessura_diastolica_septo, espessura_diastolica_ppve, 
                  relacao_septo_parede_posterior, volume_diastolico_final, volume_sistolico_final, 
                  volume_sistolico, fracao_ejecao_teichols, fracao_ejecao_simpson, fracao_ejecao, 
                  debito_cardiaco, indice_cardiaco, volume_atrio_esquerdo, massa_ve, indice_massa_ve, 
                  relacao_volume_massa, fluxo_pulmonar, gradiente_vd_ap, fluxo_aortico, gradiente_ve_ao, 
                  fluxo_mitral, gradiente_ae_ve, fluxo_tricuspide, gradiente_ad_vd, pressao_atrio_direito, psap))
        
        conn.commit()
        conn.close()
        
        flash('Parâmetros salvos com sucesso!', 'success')
        return redirect(url_for('laudo', exame_id=exame_id))

@app.route('/exame/<int:exame_id>/laudo', methods=['GET', 'POST'])
def laudo(exame_id):
    conn = get_db_connection()
    exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
    
    if exame is None:
        conn.close()
        flash('Exame não encontrado!', 'error')
        return redirect(url_for('index'))
    
    laudo = conn.execute('SELECT * FROM laudos WHERE exame_id = ?', (exame_id,)).fetchone()
    
    # Buscar médico selecionado
    try:
        medico_selecionado = conn.execute('SELECT * FROM medicos ORDER BY id DESC LIMIT 1').fetchone()
    except:
        medico_selecionado = None
    
    conn.close()
    
    return render_template('laudo.html', exame=exame, laudo=laudo, medico=medico_selecionado)

@app.route('/exame/<int:exame_id>/salvar_laudo', methods=['POST'])
def salvar_laudo(exame_id):
    if request.method == 'POST':
        resumo_exame = request.form.get('resumo_exame', '')
        medico_responsavel = request.form.get('medico_responsavel', 'Michel Raineri Haddad')
        crm_medico = request.form.get('crm_medico', 'CRM: 183299')
        ritmo_cardiaco = request.form.get('ritmo_cardiaco', '')
        ventriculo_esquerdo = request.form.get('ventriculo_esquerdo', '')
        ventriculo_direito = request.form.get('ventriculo_direito', '')
        valvas = request.form.get('valvas', '')
        pericardio = request.form.get('pericardio', '')
        aorta = request.form.get('aorta', '')
        achados_ecocardiograficos = request.form.get('achados_ecocardiograficos', '')
        conclusao = request.form.get('conclusao', '')
        observacoes = request.form.get('observacoes', '')
        signature_data = request.form.get('signature_data', '')
        
        conn = get_db_connection()
        exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
        
        if exame is None:
            conn.close()
            flash('Exame não encontrado!', 'error')
            return redirect(url_for('index'))
        
        laudo = conn.execute('SELECT * FROM laudos WHERE exame_id = ?', (exame_id,)).fetchone()
        
        if laudo:
            # Atualizar laudo existente
            conn.execute('''
            UPDATE laudos SET 
                resumo_exame = ?,
                medico_responsavel = ?,
                crm_medico = ?,
                ritmo_cardiaco = ?,
                ventriculo_esquerdo = ?,
                ventriculo_direito = ?,
                valvas = ?,
                pericardio = ?,
                aorta = ?,
                achados_ecocardiograficos = ?,
                conclusao = ?,
                observacoes = ?,
                signature_data = ?
            WHERE exame_id = ?
            ''', (resumo_exame, medico_responsavel, crm_medico, ritmo_cardiaco, ventriculo_esquerdo, 
                  ventriculo_direito, valvas, pericardio, aorta, achados_ecocardiograficos, 
                  conclusao, observacoes, signature_data, exame_id))
        else:
            # Inserir novo laudo
            conn.execute('''
            INSERT INTO laudos (
                exame_id, resumo_exame, medico_responsavel, crm_medico, ritmo_cardiaco, 
                ventriculo_esquerdo, ventriculo_direito, valvas, pericardio, aorta, 
                achados_ecocardiograficos, conclusao, observacoes, signature_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (exame_id, resumo_exame, medico_responsavel, crm_medico, ritmo_cardiaco, 
                  ventriculo_esquerdo, ventriculo_direito, valvas, pericardio, aorta, 
                  achados_ecocardiograficos, conclusao, observacoes, signature_data))
        
        conn.commit()
        conn.close()
        
        flash('Laudo salvo com sucesso!', 'success')
        return redirect(url_for('laudo', exame_id=exame_id))

# Rota para buscar modelos de laudo
@app.route('/buscar_modelos_laudo', methods=['GET'])
def buscar_modelos_laudo():
    termo = request.args.get('termo', '')
    
    conn = get_db_connection()
    
    if termo:
        # Busca por termo
        modelos = conn.execute(
            'SELECT * FROM modelos_laudo WHERE nome LIKE ? OR conteudo LIKE ? ORDER BY nome',
            (f'%{termo}%', f'%{termo}%')
        ).fetchall()
    else:
        # Buscar todos
        modelos = conn.execute('SELECT * FROM modelos_laudo ORDER BY nome').fetchall()
    
    conn.close()
    
    # Converter para lista de dicionários
    resultado = []
    for modelo in modelos:
        resultado.append({
            'id': modelo['id'],
            'nome': modelo['nome'],
            'conteudo': modelo['conteudo']
        })
    
    return jsonify(resultado)

# Rota para gerar PDF
@app.route('/exame/<int:exame_id>/gerar_pdf', methods=['GET'])
def gerar_pdf(exame_id):
    conn = get_db_connection()
    exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
    
    if exame is None:
        conn.close()
        flash('Exame não encontrado!', 'error')
        return redirect(url_for('index'))
    
    parametros = conn.execute('SELECT * FROM parametros WHERE exame_id = ?', (exame_id,)).fetchone()
    laudo = conn.execute('SELECT * FROM laudos WHERE exame_id = ?', (exame_id,)).fetchone()
    conn.close()
    
    # Renderizar o template HTML para o PDF
    html = render_template('impressao_completa.html', exame=exame, parametros=parametros, laudo=laudo)
    
    # Gerar PDF
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    # Criar resposta com o PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ecocardiograma_{exame_id}.pdf'
    
    return response

# Rota para excluir exame
@app.route('/excluir_exame/<int:exame_id>', methods=['POST'])
def excluir_exame(exame_id):
    conn = get_db_connection()
    
    # Verificar se o exame existe
    exame = conn.execute('SELECT * FROM exames WHERE id = ?', (exame_id,)).fetchone()
    
    if exame is None:
        conn.close()
        flash('Exame não encontrado!', 'error')
        return redirect(url_for('index'))
    
    # Excluir registros relacionados
    conn.execute('DELETE FROM laudos WHERE exame_id = ?', (exame_id,))
    conn.execute('DELETE FROM parametros WHERE exame_id = ?', (exame_id,))
    conn.execute('DELETE FROM exames WHERE id = ?', (exame_id,))
    
    conn.commit()
    conn.close()
    
    flash('Exame excluído com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota para buscar exames por nome de paciente (para AJAX)
@app.route('/buscar_exames', methods=['GET'])
def buscar_exames():
    termo = request.args.get('termo', '')
    
    conn = get_db_connection()
    
    if termo:
        # Busca por termo no nome do paciente
        exames = conn.execute(
            'SELECT * FROM exames WHERE nome_paciente LIKE ? ORDER BY data_criacao DESC',
            (f'%{termo}%',)
        ).fetchall()
    else:
        # Buscar todos
        exames = conn.execute('SELECT * FROM exames ORDER BY data_criacao DESC').fetchall()
    
    conn.close()
    
    # Converter para lista de dicionários
    resultado = []
    for exame in exames:
        resultado.append({
            'id': exame['id'],
            'nome_paciente': exame['nome_paciente'],
            'data_exame': exame['data_exame'],
            'idade': exame['idade'],
            'medico_solicitante': exame['medico_solicitante']
        })
    
    return jsonify(resultado)

# Rotas para cadastro e gerenciamento de médicos
@app.route('/cadastro_medico', methods=['GET', 'POST'])
def cadastro_medico():
    mensagem = None
    tipo_mensagem = None
    
    if request.method == 'POST':
        nome_medico = request.form.get('nome_medico', '')
        crm_medico = request.form.get('crm_medico', '')
        assinatura_data = request.form.get('assinatura_data', '')
        
        if not nome_medico or not crm_medico:
            mensagem = 'Nome e CRM são obrigatórios!'
            tipo_mensagem = 'danger'
        else:
            conn = get_db_connection()
            
            # Inserir novo médico
            conn.execute('''
            INSERT INTO medicos (nome, crm, assinatura_data)
            VALUES (?, ?, ?)
            ''', (nome_medico, crm_medico, assinatura_data))
            
            conn.commit()
            
            # Obter o ID do médico recém-cadastrado
            medico_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            conn.close()
            
            mensagem = 'Médico cadastrado com sucesso!'
            tipo_mensagem = 'success'
            
            # Redirecionar para a seleção do médico
            return redirect(url_for('selecionar_medico', medico_id=medico_id))
    
    # Buscar médicos cadastrados
    conn = get_db_connection()
    try:
        medicos = conn.execute('SELECT * FROM medicos ORDER BY nome').fetchall()
    except:
        # Se a tabela não existir, criar
        conn.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT NOT NULL,
            assinatura_data TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        medicos = []
    
    # Verificar se há um médico selecionado
    medico_selecionado = None
    medico_selecionado_id = request.args.get('medico_selecionado')
    
    if medico_selecionado_id:
        try:
            medico_selecionado = conn.execute('SELECT id FROM medicos WHERE id = ?', 
                                         (medico_selecionado_id,)).fetchone()
        except:
            medico_selecionado = None
    
    conn.close()
    
    # Converter para lista de dicionários para o template
    medicos_lista = []
    for medico in medicos:
        medicos_lista.append({
            'id': medico['id'],
            'nome': medico['nome'],
            'crm': medico['crm'],
            'assinatura_url': medico['assinatura_data']
        })
    
    return render_template('cadastro_medico.html', 
                          medicos=medicos_lista, 
                          medico_selecionado=medico_selecionado_id if medico_selecionado else None,
                          mensagem=mensagem,
                          tipo_mensagem=tipo_mensagem)

@app.route('/selecionar_medico/<int:medico_id>')
def selecionar_medico(medico_id):
    conn = get_db_connection()
    try:
        medico = conn.execute('SELECT * FROM medicos WHERE id = ?', (medico_id,)).fetchone()
    except:
        conn.close()
        flash('Erro ao acessar tabela de médicos!', 'error')
        return redirect(url_for('index'))
    
    if medico is None:
        conn.close()
        flash('Médico não encontrado!', 'error')
        return redirect(url_for('cadastro_medico'))
    
    conn.close()
    
    flash(f'Médico {medico["nome"]} selecionado com sucesso!', 'success')
    return redirect(url_for('cadastro_medico', medico_selecionado=medico_id))

@app.route('/obter_assinatura_medico/<int:medico_id>')
def obter_assinatura_medico(medico_id):
    conn = get_db_connection()
    try:
        medico = conn.execute('SELECT * FROM medicos WHERE id = ?', (medico_id,)).fetchone()
    except:
        conn.close()
        return jsonify({'success': False, 'message': 'Erro ao acessar tabela de médicos'})
    
    if medico is None:
        conn.close()
        return jsonify({'success': False, 'message': 'Médico não encontrado'})
    
    conn.close()
    
    return jsonify({
        'success': True,
        'signature_data': medico['assinatura_data']
    })

@app.route('/medico_atual')
def medico_atual():
    conn = get_db_connection()
    try:
        medico = conn.execute('SELECT * FROM medicos ORDER BY id DESC LIMIT 1').fetchone()
    except:
        conn.close()
        return jsonify({
            'success': False,
            'message': 'Erro ao acessar tabela de médicos'
        })
    
    conn.close()
    
    if medico is None:
        return jsonify({
            'success': False,
            'message': 'Nenhum médico cadastrado'
        })
    
    return jsonify({
        'success': True,
        'medico': {
            'id': medico['id'],
            'nome': medico['nome'],
            'crm': medico['crm'],
            'assinatura_data': medico['assinatura_data']
        }
    })


# Rotas para busca de modelos são gerenciadas pelo integrador_modelos
# Removidas daqui para evitar conflito de endpoints


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
