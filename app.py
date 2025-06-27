import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vidah-echo-system-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database with enhanced stability
database_url = os.environ.get("DATABASE_URL", "sqlite:///ecocardiograma.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Enhanced database configuration for stability
if database_url.startswith('postgresql'):
    # PostgreSQL specific optimizations
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 3600,  # 1 hour
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "echo": False  # Set to True for SQL debugging
    }
else:
    # SQLite specific optimizations
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "check_same_thread": False,
            "timeout": 20
        }
    }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Faça login para acessar esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from auth.models import AuthUser
    return AuthUser.query.get(int(user_id))

# Make current_user available in all templates
@app.context_processor
def inject_user():
    from flask_login import current_user
    return dict(current_user=current_user)

with app.app_context():
    # Import models to ensure tables are created
    import models
    from auth.models import AuthUser, UserSession
    db.create_all()
    
    # Register authentication blueprint
    from auth.blueprints import auth_bp
    app.register_blueprint(auth_bp)
    
    # Initialize security middleware
    from auth.security import RequestSecurityMiddleware
    security_middleware = RequestSecurityMiddleware(app)
    
    # Configurar sistema de logging centralizado
    from utils.logging_system import configurar_logging, log_system_startup
    
    # Configurar logger
    system_logger = configurar_logging(app, db)
    
    # Registrar inicialização do sistema
    log_system_startup()
    
    logging.info("Database tables created successfully")
    logging.info("Sistema de logging centralizado configurado")
    
    # Inicializar sistema de backup automático
    try:
        from utils.backup_scheduler import init_backup_scheduler
        init_backup_scheduler()
        logging.info('Sistema de backup automático iniciado')
    except Exception as e:
        logging.error(f'Erro ao inicializar backup automático: {e}')
