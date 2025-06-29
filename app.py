import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Criar a aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vidah-sistema-2025-secreto")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configurar banco de dados
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///ecocardiograma.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar extensões
db.init_app(app)

with app.app_context():
    try:
        # Importar models
        import models
        
        # Criar tabelas
        db.create_all()
        logging.info("Tabelas criadas com sucesso")
        
        # Criar usuário admin se não existir
        from models import Usuario
        from werkzeug.security import generate_password_hash
        
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = Usuario(
                username='admin',
                email='admin@grupovidah.com.br',
                password_hash=generate_password_hash('VidahAdmin2025!'),
                is_admin=True
            )
            db.session.add(admin_user)
            logging.info("Usuário admin criado")
        
        # Criar usuário padrão se não existir
        user_default = Usuario.query.filter_by(username='usuario').first()
        if not user_default:
            user_default = Usuario(
                username='usuario',
                email='usuario@grupovidah.com.br',
                password_hash=generate_password_hash('Usuario123!'),
                is_admin=False
            )
            db.session.add(user_default)
            logging.info("Usuário padrão criado")
        
        # Criar médico padrão se não existir
        from models import Medico
        medico_default = Medico.query.filter_by(nome='Michel Raineri Haddad').first()
        if not medico_default:
            medico_default = Medico(
                nome='Michel Raineri Haddad',
                crm='CRM-SP 183299',
                especialidade='Cardiologia',
                email='michel@grupovidah.com.br',
                ativo=True
            )
            db.session.add(medico_default)
            logging.info("Médico padrão criado")
        
        db.session.commit()
        logging.info("Inicialização do banco concluída")
        
    except ImportError as e:
        logging.error(f"Erro ao importar models: {e}")
        db.create_all()
    except Exception as e:
        logging.error(f"Erro na inicialização: {e}")
        db.session.rollback()

# Importar rotas
try:
    import routes
    logging.info("Rotas importadas com sucesso")
except ImportError as e:
    logging.error(f"Erro ao importar rotas: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
