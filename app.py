```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.secret_key = os.environ.get("SESSION_SECRET", "vidah-secret-key-2025")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ecocardiograma.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Middleware para proxy reverso
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import Usuario
        return Usuario.query.get(int(user_id))
    
    with app.app_context():
        # Importar modelos
        import models
        
        # Criar tabelas
        db.create_all()
        
        # Criar usuários padrão se não existirem
        from models import Usuario
        from werkzeug.security import generate_password_hash
        
        # Usuário admin
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = Usuario()
            admin_user.username = 'admin'
            admin_user.email = 'admin@grupovidah.com.br'
            admin_user.role = 'admin'
            admin_user.ativo = True
            admin_user.set_password('VidahAdmin2025!')
            db.session.add(admin_user)
        
        # Usuário comum
        user = Usuario.query.filter_by(username='usuario').first()
        if not user:
            user = Usuario()
            user.username = 'usuario'
            user.email = 'usuario@grupovidah.com.br'
            user.role = 'user'
            user.ativo = True
            user.set_password('Usuario123!')
            db.session.add(user)
        
        # Médico padrão
        from models import Medico
        medico = Medico.query.filter_by(crm='183299').first()
        if not medico:
            medico = Medico()
            medico.nome = 'Dr. Michel Raineri Haddad'
            medico.crm = '183299'
            medico.ativo = True
            db.session.add(medico)
        
        try:
            db.session.commit()
            print("✅ Banco de dados inicializado com sucesso")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao inicializar banco: {e}")
    
    return app

# Criar a aplicação
app = create_app()

# Importar rotas
import routes
```
