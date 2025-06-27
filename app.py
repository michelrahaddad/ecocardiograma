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
login_manager.login_view = 'auth_login'
login_manager.login_message = 'Acesso negado. Faça login para continuar.'
login_manager.login_message_category = 'info'

with app.app_context():
    # Import models and routes
    try:
        import models
        db.create_all()
        
        # Configure user loader
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return models.Usuario.query.get(int(user_id))
            except:
                return None
                
    except ImportError:
        pass
    
    try:
        import routes
    except ImportError:
        pass
