from datetime import datetime, timezone, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Fuso horário de Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))

def datetime_brasilia():
    """Retorna datetime atual no fuso horário de Brasília"""
    return datetime.now(BRASILIA_TZ)

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
    
    # Relacionamento com parâmetros
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
    
    # Medidas ecocardiográficas básicas
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
    
    # Velocidades dos fluxos valvulares
    fluxo_pulmonar = db.Column(db.Float)
    fluxo_mitral = db.Column(db.Float)
    fluxo_aortico = db.Column(db.Float)
    fluxo_tricuspide = db.Column(db.Float)
    

    
    # Gradientes específicos
    gradiente_vd_ap = db.Column(db.Float)  # Ventrículo Direito → Artéria Pulmonar
    gradiente_ae_ve = db.Column(db.Float)  # Átrio Esquerdo → Ventrículo Esquerdo
    gradiente_ve_ao = db.Column(db.Float)  # Ventrículo Esquerdo → Aorta
    gradiente_ad_vd = db.Column(db.Float)  # Átrio Direito → Ventrículo Direito
    
    # Gradientes e PSAP
    gradiente_tricuspide = db.Column(db.Float)
    pressao_sistolica_vd = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)

class LaudoEcocardiograma(db.Model):
    __tablename__ = 'laudos_ecocardiograma'
    
    id = db.Column(db.Integer, primary_key=True)
    exame_id = db.Column(db.Integer, db.ForeignKey('exames.id'), nullable=False)
    
    # Seções do laudo
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
    
    @property
    def is_active(self):
        """Necessário para Flask-Login"""
        return bool(self.ativo)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class LogSistema(db.Model):
    __tablename__ = 'logs_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    nivel = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    mensagem = db.Column(db.Text, nullable=False)
    modulo = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)

class BackupSistema(db.Model):
    __tablename__ = 'backups_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(200), nullable=False)
    tamanho_arquivo = db.Column(db.BigInteger)
    tipo_backup = db.Column(db.String(50))  # COMPLETO, INCREMENTAL
    status = db.Column(db.String(20), default='CONCLUIDO')
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)

class PatologiaLaudo(db.Model):
    __tablename__ = 'patologias_laudo'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, unique=True)
    categoria = db.Column(db.String(100))  # Ex: Cardiomiopatias, Valvopatias, etc.
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    
    # Relacionamentos
    templates_laudo = db.relationship('TemplateLaudo', backref='patologia', cascade='all, delete-orphan')

class TemplateLaudo(db.Model):
    __tablename__ = 'templates_laudo'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    patologia_id = db.Column(db.Integer, db.ForeignKey('patologias_laudo.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('medicos.id'), nullable=True)  # NULL = template global
    
    # Conteúdo dos templates
    modo_m_bidimensional = db.Column(db.Text)
    doppler_convencional = db.Column(db.Text)
    doppler_tecidual = db.Column(db.Text)
    conclusao = db.Column(db.Text)
    
    # Configurações
    publico = db.Column(db.Boolean, default=False)  # Se outros médicos podem usar
    favorito = db.Column(db.Boolean, default=False)
    vezes_usado = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    
    def to_dict(self):
        # Buscar patologia e médico por ID para evitar erro de relacionamento
        patologia_nome = None
        medico_nome = 'Template Global'
        
        try:
            if self.patologia_id:
                patologia = PatologiaLaudo.query.get(self.patologia_id)
                if patologia:
                    patologia_nome = patologia.nome
        except:
            patologia_nome = 'Patologia não encontrada'
            
        try:
            if self.medico_id:
                medico = Medico.query.get(self.medico_id)
                if medico:
                    medico_nome = medico.nome
        except:
            medico_nome = 'Médico não encontrado'
        
        # Formatar data em horário de Brasília
        created_at_formatted = 'Data não disponível'
        if self.created_at:
            try:
                # Converter para timezone de Brasília
                brasilia_tz = timezone(timedelta(hours=-3))
                if self.created_at.tzinfo is None:
                    # Se não tem timezone, assume UTC e converte para Brasília
                    created_at_brasilia = self.created_at.replace(tzinfo=timezone.utc).astimezone(brasilia_tz)
                else:
                    created_at_brasilia = self.created_at.astimezone(brasilia_tz)
                created_at_formatted = created_at_brasilia.strftime('%d/%m/%Y às %H:%M')
            except Exception:
                # Se houver erro na conversão, usar timestamp atual
                now_brasilia = datetime.now(timezone(timedelta(hours=-3)))
                created_at_formatted = now_brasilia.strftime('%d/%m/%Y às %H:%M')
        
        return {
            'id': self.id,
            'nome': self.nome,
            'patologia_nome': patologia_nome,
            'medico_nome': medico_nome,
            'modo_m_bidimensional': self.modo_m_bidimensional or '',
            'doppler_convencional': self.doppler_convencional or '',
            'doppler_tecidual': self.doppler_tecidual or '',
            'conclusao': self.conclusao or '',
            'publico': self.publico,
            'favorito': self.favorito,
            'vezes_usado': self.vezes_usado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_at_formatted': created_at_formatted or 'Data não disponível'
        }

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
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime_brasilia)
    updated_at = db.Column(db.DateTime, default=datetime_brasilia, onupdate=datetime_brasilia)
    
    def __init__(self, **kwargs):
        """Constructor para LaudoTemplate com argumentos nomeados"""
        self.categoria = kwargs.get('categoria', 'Adulto')
        self.diagnostico = kwargs.get('diagnostico', '')
        self.modo_m_bidimensional = kwargs.get('modo_m_bidimensional', '')
        self.doppler_convencional = kwargs.get('doppler_convencional', '')
        self.doppler_tecidual = kwargs.get('doppler_tecidual', '')
        self.conclusao = kwargs.get('conclusao', '')
        self.ativo = kwargs.get('ativo', True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'categoria': self.categoria,
            'diagnostico': self.diagnostico,
            'modo_m_bidimensional': self.modo_m_bidimensional,
            'doppler_convencional': self.doppler_convencional,
            'doppler_tecidual': self.doppler_tecidual,
            'conclusao': self.conclusao,
            'ativo': self.ativo
        }
