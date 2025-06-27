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
app.secret_key = os.environ.get("SESSION_SECRET", "vidah-echo-system-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "sqlite:///ecocardiograma.db"

# Enhanced database configuration for production
if database_url and database_url.startswith('postgresql'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "echo": False  # Disable SQL logging in production
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

# Initialize the application with proper error handling
def initialize_app():
    """Initialize app with database and auth setup"""
    with app.app_context():
        try:
            print("🚀 Iniciando aplicação...")
            
            # Import models first
            import models
            from auth.models import AuthUser
            
            print("📊 Criando tabelas no banco...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Configure user loader for AuthUser
            @login_manager.user_loader
            def load_user(user_id):
                try:
                    return AuthUser.query.get(int(user_id))
                except Exception as e:
                    print(f"❌ Erro ao carregar usuário {user_id}: {e}")
                    return None
            
            # Check if system needs initialization
            try:
                admin_count = AuthUser.query.filter_by(role='admin').count()
                print(f"👑 Administradores encontrados: {admin_count}")
                
                if admin_count == 0:
                    print("🔧 Inicializando sistema com usuários padrão...")
                    
                    from werkzeug.security import generate_password_hash
                    
                    # Create admin user
                    admin_user = AuthUser(
                        username='admin',
                        email='admin@grupovida.com.br',
                        password_hash=generate_password_hash('VidahAdmin2025!'),
                        role='admin',
                        is_active_flag=True,
                        is_verified=True
                    )
                    
                    # Create regular user  
                    regular_user = AuthUser(
                        username='usuario',
                        email='usuario@grupovida.com.br',
                        password_hash=generate_password_hash('Usuario123!'),
                        role='user',
                        is_active_flag=True,
                        is_verified=True
                    )
                    
                    db.session.add(admin_user)
                    db.session.add(regular_user)
                    db.session.commit()
                    
                    print("✅ Usuários padrão criados:")
                    print("   👑 Admin: admin / VidahAdmin2025!")
                    print("   👤 User: usuario / Usuario123!")
                else:
                    print("✅ Sistema já inicializado!")
                    
            except Exception as e:
                print(f"⚠️  Erro ao verificar/criar usuários: {e}")
                db.session.rollback()
                
            print("🎉 Aplicação inicializada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro crítico na inicialização: {e}")
            import traceback
            traceback.print_exc()
            
        try:
            # Import routes last
            import routes
            print("🛣️  Rotas carregadas com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar rotas: {e}")
            import traceback
            traceback.print_exc()

# Initialize when module is imported
initialize_app()
