import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Create database instance
db = SQLAlchemy()

# Create login manager
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vidah-echo-system-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///ecocardiograma.db"

# Enhanced database configuration
if database_url and database_url.startswith('postgresql'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Acesso negado. Faça login para continuar.'
login_manager.login_message_category = 'info'

with app.app_context():
    # Import models and routes
    try:
        import models
        from models import Usuario
        
        # Create all tables
        db.create_all()
        
        # Configure user loader for Usuario
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return Usuario.query.get(int(user_id))
            except:
                return None
        
        # Initialize system with admin user if needed
        try:
            admin_exists = Usuario.query.filter_by(role='admin').first()
            if not admin_exists:
                # Create admin user
                admin_user = Usuario(
                    username='admin',
                    email='admin@grupovida.com.br',
                    role='admin',
                    ativo=True
                )
                admin_user.set_password('VidahAdmin2025!')
                
                # Create regular user
                regular_user = Usuario(
                    username='usuario',
                    email='usuario@grupovida.com.br',
                    role='user',
                    ativo=True
                )
                regular_user.set_password('Usuario123!')
                
                db.session.add(admin_user)
                db.session.add(regular_user)
                db.session.commit()
                
                print("Sistema inicializado com usuários padrão:")
                print("Admin: admin / VidahAdmin2025!")
                print("Usuário: usuario / Usuario123!")
                
        except Exception as e:
            print(f"Erro ao inicializar usuários: {e}")
            db.session.rollback()
                
    except ImportError as e:
        print(f"Erro ao importar modelos: {e}")
    
    try:
        import routes
    except ImportError as e:
        print(f"Erro ao importar rotas: {e}")
