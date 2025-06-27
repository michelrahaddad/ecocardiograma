from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

def datetime_brasilia():
    """Retorna datetime atual no fuso horário de Brasília"""
    brasil_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasil_tz)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50), default='user')  # 'user' ou 'admin'
    ativo = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    
    def set_password(self, password):
        """Define a senha do usuário com hash seguro"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role == 'admin'
    
    def is_active(self):
        """Necessário para Flask-Login"""
        return self.ativo
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Exame(db.Model):
    __tablename__ = 'exames'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_paciente = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    data_exame = db.Column(db.String(10), nullable=False)
    tipo_atendimento = db.Column(db.String(50))
    medico_usuario = db.Column(db.String(200))
    medico_solicitante = db.Column(db.String(200))
    indicacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    
    # Relacionamentos
    parametros = db.relationship('ParametrosEcocardiograma', backref='exame', uselist=False, cascade='all, delete-orphan')
    laudos = db.relationship('LaudoEcocardiograma', backref='exame', cascade='all, delete-orphan')

class ParametrosEcocardiograma(db.Model):
    __tablename__ = 'parametros_ecocardiograma'
    
    id = db.Column(db.Integer, primary_key=True)
    exame_id = db.Column(db.Integer, db.ForeignKey('exames.id'), nullable=False)
    
    # Dados antropométricos
    peso = db.Column(db.Float)
    altura = db.Column(db.Float)
    superficie_corporal = db.Column(db.Float)
    frequencia_cardiaca = db.Column(db.Integer)
    
    # Medidas básicas
    atrio_esquerdo = db.Column(db.Float)
    raiz_aorta = db.Column(db.Float)
    relacao_atrio_esquerdo_aorta = db.Column(db.Float)
    aorta_ascendente = db.Column(db.Float)
    diametro_ventricular_direito = db.Column(db.Float)
    diametro_basal_vd = db.Column(db.Float)
    
    # Ventrículo esquerdo
    diametro_diastolico_final_ve = db.Column(db.Float)
    diametro_sistolico_final = db.Column(db.Float)
    percentual_encurtamento = db.Column(db.Float)
    espessura_diastolica_septo = db.Column(db.Float)
    espessura_diastolica_ppve = db.Column(db.Float)
    relacao_septo_parede_posterior = db.Column(db.Float)
    
    # Volumes e função sistólica
    volume_diastolico_final = db.Column(db.Float)
    volume_sistolico_final = db.Column(db.Float)
    volume_ejecao = db.Column(db.Float)
    fracao_ejecao = db.Column(db.Float)
    indice_massa_ve = db.Column(db.Float)
    massa_ve = db.Column(db.Float)
    
    # Velocidades dos fluxos
    fluxo_pulmonar = db.Column(db.Float)
    fluxo_mitral = db.Column(db.Float)
    fluxo_aortico = db.Column(db.Float)
    fluxo_tricuspide = db.Column(db.Float)
    
    # Gradientes
    gradiente_vd_ap = db.Column(db.Float)  # Ventrículo Direito → Artéria Pulmonar
    gradiente_ae_ve = db.Column(db.Float)  # Átrio Esquerdo → Ventrículo Esquerdo
    gradiente_ve_ao = db.Column(db.Float)  # Ventrículo Esquerdo → Aorta
    gradiente_ad_vd = db.Column(db.Float)  # Átrio Direito → Ventrículo Direito
    
    # Insuficiência tricúspide e PSAP
    gradiente_tricuspide = db.Column(db.Float)
    pressao_sistolica_vd = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)

class LaudoEcocardiograma(db.Model):
    __tablename__ = 'laudos_ecocardiograma'
    
    id = db.Column(db.Integer, primary_key=True)
    exame_id = db.Column(db.Integer, db.ForeignKey('exames.id'), nullable=False)
    
    modo_m_bidimensional = db.Column(db.Text)
    doppler_convencional = db.Column(db.Text)
    doppler_tecidual = db.Column(db.Text)
    conclusao = db.Column(db.Text)
    recomendacoes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)

class Medico(db.Model):
    __tablename__ = 'medicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    crm = db.Column(db.String(50), nullable=False)
    assinatura_data = db.Column(db.Text)  # Base64 da assinatura
    assinatura_url = db.Column(db.String(500))  # URL para a imagem da assinatura
    ativo = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)

class LogSistema(db.Model):
    __tablename__ = 'logs_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    mensagem = db.Column(db.Text, nullable=False)
    modulo = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)

class LaudoTemplate(db.Model):
    __tablename__ = 'laudos_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)  # Adulto, Pediátrico
    diagnostico = db.Column(db.String(200), nullable=False)
    modo_m_bidimensional = db.Column(db.Text)
    doppler_convencional = db.Column(db.Text)
    doppler_tecidual = db.Column(db.Text)
    conclusao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
