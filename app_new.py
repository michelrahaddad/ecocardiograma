"""
Aplicação Flask Modular - Sistema de Ecocardiograma

Aplicação refatorada com arquitetura modular, eliminando código duplicado
e implementando padrões anti-bug.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Inicializar extensões
db = SQLAlchemy(model_class=Base)

def create_app(config=None):
    """Factory para criar aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    configure_app(app, config)
    
    # Inicializar extensões
    initialize_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar handlers de erro
    configure_error_handlers(app)
    
    # Criar tabelas do banco
    create_database_tables(app)
    
    logger.info("Aplicação Flask criada com sucesso")
    return app

def configure_app(app, config=None):
    """Configurar aplicação Flask"""
    # Configurações básicas
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ecocardiograma.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Configurações de upload
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
    app.config["UPLOAD_FOLDER"] = "uploads"
    
    # ProxyFix para deployments
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configurações adicionais
    if config:
        app.config.update(config)
    
    logger.info("Configurações da aplicação carregadas")

def initialize_extensions(app):
    """Inicializar extensões Flask"""
    db.init_app(app)
    logger.info("Extensões inicializadas")

def register_blueprints(app):
    """Registrar blueprints modulares"""
    from routes_new import main_bp, exams_bp, reports_bp, maintenance_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(exams_bp, url_prefix='/exames')
    app.register_blueprint(reports_bp, url_prefix='/relatorios')
    app.register_blueprint(maintenance_bp, url_prefix='/manutencao')
    
    logger.info("Blueprints registrados")

def configure_error_handlers(app):
    """Configurar handlers de erro personalizados"""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"Página não encontrada: {error}")
        return render_template('500.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno: {error}")
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception(f"Exceção não tratada: {e}")
        db.session.rollback()
        return render_template('500.html'), 500

def create_database_tables(app):
    """Criar tabelas do banco de dados"""
    with app.app_context():
        try:
            import models
            db.create_all()
            logger.info("Tabelas do banco criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise

# Criar instância da aplicação
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)