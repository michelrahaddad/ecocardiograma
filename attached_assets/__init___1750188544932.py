"""
Módulo de Integração de Manutenção

Este módulo integra todas as funções de manutenção ao sistema principal.
"""

import os
import logging

# Importar módulos de manutenção
from manutencao.atualizacao import adicionar_rotas_atualizacao, verificar_atualizacoes_ao_iniciar
from manutencao.backup import adicionar_rotas_backup, verificar_backup_automatico_ao_iniciar
from manutencao.logs import adicionar_rotas_logs, configurar_logs_aplicacao
from manutencao.diagnostico import adicionar_rotas_diagnostico, configurar_diagnostico_aplicacao
from manutencao.integridade import adicionar_rotas_integridade, verificar_integridade_ao_iniciar
from manutencao.limpeza import adicionar_rotas_limpeza, verificar_limpeza_automatica_ao_iniciar
from manutencao.usuarios import adicionar_rotas_usuarios, configurar_autenticacao
from manutencao.instalador import adicionar_rotas_instalador

# Configuração do logger
logger = logging.getLogger('manutencao')

def configurar_manutencao(app):
    """
    Configura todas as funções de manutenção para a aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    # Configurar diretórios necessários
    diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(diretorio_base, "config"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "logs"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "backups"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "backups", "sistema"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "backups", "atualizacoes"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "diagnostico"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "integridade"), exist_ok=True)
    os.makedirs(os.path.join(diretorio_base, "instalador"), exist_ok=True)
    
    # Configurar logger
    log_dir = os.path.join(diretorio_base, "logs")
    log_file = os.path.join(log_dir, "manutencao.log")
    
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    logger.info("Configurando funções de manutenção...")
    
    try:
        # Configurar logs
        configurar_logs_aplicacao(app)
        
        # Configurar autenticação
        configurar_autenticacao(app)
        
        # Configurar verificações automáticas
        verificar_atualizacoes_ao_iniciar(app)
        verificar_backup_automatico_ao_iniciar(app)
        verificar_integridade_ao_iniciar(app)
        verificar_limpeza_automatica_ao_iniciar(app)
        configurar_diagnostico_aplicacao(app)
        
        # Adicionar rotas
        adicionar_rotas_atualizacao(app)
        adicionar_rotas_backup(app)
        adicionar_rotas_logs(app)
        adicionar_rotas_diagnostico(app)
        adicionar_rotas_integridade(app)
        adicionar_rotas_limpeza(app)
        adicionar_rotas_usuarios(app)
        adicionar_rotas_instalador(app)
        
        # Adicionar rota principal de manutenção
        @app.route('/manutencao')
        def pagina_manutencao():
            from flask import render_template
            return render_template('manutencao/index.html')
        
        logger.info("Funções de manutenção configuradas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao configurar funções de manutenção: {str(e)}")
        raise
