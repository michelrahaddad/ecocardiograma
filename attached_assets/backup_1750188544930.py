"""
Módulo de Backup e Restauração

Este módulo implementa um sistema de backup e restauração para o software de ecocardiograma.
Permite criar, gerenciar e restaurar backups do banco de dados e arquivos de configuração.
"""

import os
import json
import sqlite3
import shutil
import logging
import zipfile
import tempfile
from datetime import datetime

# Configuração do logger
logger = logging.getLogger('sistema_backup')

class SistemaBackup:
    def __init__(self):
        """
        Inicializa o sistema de backup e restauração.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_backup = os.path.join(self.diretorio_base, "backups", "sistema")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "backup.json")
        self.arquivo_db = os.path.join(self.diretorio_base, "ecocardiograma.db")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_backup, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de backup."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "backup.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de backup."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "backup_automatico": True,
                "intervalo_dias": 7,
                "ultima_execucao": None,
                "max_backups": 10,
                "incluir_logs": False,
                "compressao": True,
                "backups": []
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de backup criado")
    
    def criar_backup(self, descricao="Backup manual"):
        """
        Cria um backup completo do sistema.
        
        Args:
            descricao: Descrição do backup
            
        Returns:
            str: Caminho para o arquivo de backup ou None em caso de erro
        """
        logger.info(f"Criando backup: {descricao}")
        
        try:
            # Verificar se o banco de dados existe
            if not os.path.exists(self.arquivo_db):
                logger.error("Banco de dados não encontrado")
                return None
            
            # Criar nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backup_{timestamp}.zip"
            caminho_backup = os.path.join(self.diretorio_backup, nome_backup)
            
            # Criar diretório temporário para o backup
            diretorio_temp = tempfile.mkdtemp()
            
            # Copiar banco de dados para o diretório temporário
            db_backup_path = os.path.join(diretorio_temp, "ecocardiograma.db")
            
            # Fazer uma cópia segura do banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            backup_conn = sqlite3.connect(db_backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            
            # Copiar arquivos de configuração
            config_dir = os.path.join(self.diretorio_base, "config")
            if os.path.exists(config_dir):
                config_backup_dir = os.path.join(diretorio_temp, "config")
                os.makedirs(config_backup_dir, exist_ok=True)
                
                for arquivo in os.listdir(config_dir):
                    shutil.copy2(
                        os.path.join(config_dir, arquivo),
                        os.path.join(config_backup_dir, arquivo)
                    )
            
            # Copiar modelos de laudo
            modelos_dir = os.path.join(self.diretorio_base, "src", "modelos_laudo")
            if os.path.exists(modelos_dir):
                modelos_backup_dir = os.path.join(diretorio_temp, "modelos_laudo")
                os.makedirs(modelos_backup_dir, exist_ok=True)
                
                for arquivo in os.listdir(modelos_dir):
                    shutil.copy2(
                        os.path.join(modelos_dir, arquivo),
                        os.path.join(modelos_backup_dir, arquivo)
                    )
            
            # Incluir logs se configurado
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if config.get("incluir_logs", False):
                logs_dir = os.path.join(self.diretorio_base, "logs")
                if os.path.exists(logs_dir):
                    logs_backup_dir = os.path.join(diretorio_temp, "logs")
                    os.makedirs(logs_backup_dir, exist_ok=True)
                    
                    for arquivo in os.listdir(logs_dir):
                        shutil.copy2(
                            os.path.join(logs_dir, arquivo),
                            os.path.join(logs_backup_dir, arquivo)
                        )
            
            # Criar arquivo de metadados do backup
            metadados = {
                "data": datetime.now().isoformat(),
                "descricao": descricao,
                "versao_sistema": "1.0.0",  # Obter de algum lugar
                "arquivos_incluidos": [
                    "ecocardiograma.db",
                    "config/*",
                    "modelos_laudo/*"
                ]
            }
            
            if config.get("incluir_logs", False):
                metadados["arquivos_incluidos"].append("logs/*")
            
            with open(os.path.join(diretorio_temp, "backup_info.json"), 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=4)
            
            # Criar arquivo ZIP com o conteúdo do diretório temporário
            with zipfile.ZipFile(caminho_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(diretorio_temp):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, diretorio_temp)
                        zipf.write(file_path, arcname)
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            # Atualizar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config["ultima_execucao"] = datetime.now().isoformat()
            config["backups"].append({
                "arquivo": nome_backup,
                "data": datetime.now().isoformat(),
                "descricao": descricao,
                "tamanho_bytes": os.path.getsize(caminho_backup)
            })
            
            # Limitar número de backups
            if len(config["backups"]) > config["max_backups"]:
                backups_excedentes = len(config["backups"]) - config["max_backups"]
                for i in range(backups_excedentes):
                    backup_antigo = config["backups"].pop(0)
                    arquivo_antigo = os.path.join(self.diretorio_backup, backup_antigo["arquivo"])
                    if os.path.exists(arquivo_antigo):
                        os.remove(arquivo_antigo)
                        logger.info(f"Backup antigo removido: {backup_antigo['arquivo']}")
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Backup criado com sucesso: {caminho_backup}")
            return caminho_backup
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None
    
    def restaurar_backup(self, arquivo_backup):
        """
        Restaura um backup.
        
        Args:
            arquivo_backup: Caminho para o arquivo de backup
            
        Returns:
            bool: True se a restauração for bem-sucedida, False caso contrário
        """
        logger.info(f"Restaurando backup de {arquivo_backup}...")
        
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo_backup):
                logger.error(f"Arquivo de backup não encontrado: {arquivo_backup}")
                return False
            
            # Criar backup do estado atual antes de restaurar
            backup_pre_restauracao = self.criar_backup("Backup automático pré-restauração")
            if not backup_pre_restauracao:
                logger.warning("Não foi possível criar backup pré-restauração")
            
            # Extrair backup para diretório temporário
            diretorio_temp = tempfile.mkdtemp()
            
            with zipfile.ZipFile(arquivo_backup, 'r') as zip_ref:
                zip_ref.extractall(diretorio_temp)
            
            # Verificar se o banco de dados está no backup
            db_backup_path = os.path.join(diretorio_temp, "ecocardiograma.db")
            if not os.path.exists(db_backup_path):
                logger.error("Banco de dados não encontrado no backup")
                shutil.rmtree(diretorio_temp)
                return False
            
            # Fechar todas as conexões com o banco de dados atual
            # Isso é uma simulação, em um ambiente real seria necessário garantir que não há conexões ativas
            
            # Restaurar banco de dados
            if os.path.exists(self.arquivo_db):
                os.remove(self.arquivo_db)
            
            shutil.copy2(db_backup_path, self.arquivo_db)
            
            # Restaurar arquivos de configuração
            config_backup_dir = os.path.join(diretorio_temp, "config")
            if os.path.exists(config_backup_dir):
                config_dir = os.path.join(self.diretorio_base, "config")
                os.makedirs(config_dir, exist_ok=True)
                
                for arquivo in os.listdir(config_backup_dir):
                    # Não sobrescrever o arquivo de configuração de backup
                    if arquivo == "backup.json":
                        continue
                    
                    shutil.copy2(
                        os.path.join(config_backup_dir, arquivo),
                        os.path.join(config_dir, arquivo)
                    )
            
            # Restaurar modelos de laudo
            modelos_backup_dir = os.path.join(diretorio_temp, "modelos_laudo")
            if os.path.exists(modelos_backup_dir):
                modelos_dir = os.path.join(self.diretorio_base, "src", "modelos_laudo")
                os.makedirs(modelos_dir, exist_ok=True)
                
                # Limpar diretório de modelos
                for arquivo in os.listdir(modelos_dir):
                    os.remove(os.path.join(modelos_dir, arquivo))
                
                # Copiar modelos do backup
                for arquivo in os.listdir(modelos_backup_dir):
                    shutil.copy2(
                        os.path.join(modelos_backup_dir, arquivo),
                        os.path.join(modelos_dir, arquivo)
                    )
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            logger.info("Backup restaurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return False
    
    def listar_backups(self):
        """
        Lista todos os backups disponíveis.
        
        Returns:
            list: Lista de backups
        """
        try:
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config.get("backups", [])
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []
    
    def verificar_backup_automatico(self):
        """
        Verifica se é necessário realizar um backup automático.
        
        Returns:
            bool: True se um backup automático foi realizado, False caso contrário
        """
        try:
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar se o backup automático está ativado
            if not config.get("backup_automatico", True):
                return False
            
            # Verificar a data do último backup
            ultima_execucao = config.get("ultima_execucao")
            if not ultima_execucao:
                # Nunca foi feito um backup, fazer agora
                self.criar_backup("Backup automático inicial")
                return True
            
            # Converter para datetime
            ultima_data = datetime.fromisoformat(ultima_execucao)
            agora = datetime.now()
            
            # Calcular diferença em dias
            diferenca_dias = (agora - ultima_data).days
            
            # Verificar se passou o intervalo configurado
            if diferenca_dias >= config.get("intervalo_dias", 7):
                self.criar_backup("Backup automático programado")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar backup automático: {str(e)}")
            return False

# Função para integração com a aplicação principal
def verificar_backup_automatico_ao_iniciar(app):
    """
    Função para verificar e executar backup automático ao iniciar a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.before_first_request
    def verificar_backup():
        try:
            sistema_backup = SistemaBackup()
            sistema_backup.verificar_backup_automatico()
        except Exception as e:
            # Registrar erro, mas não interromper a inicialização
            print(f"Erro ao verificar backup automático: {str(e)}")

# Adicionar rotas para o sistema de backup
def adicionar_rotas_backup(app):
    """
    Adiciona rotas para o sistema de backup à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify, send_file
    
    @app.route('/manutencao/backup')
    def pagina_backup():
        sistema_backup = SistemaBackup()
        
        # Carregar configuração
        with open(sistema_backup.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Listar backups
        backups = sistema_backup.listar_backups()
        
        return jsonify({
            "configuracoes": {
                "backup_automatico": config["backup_automatico"],
                "intervalo_dias": config["intervalo_dias"],
                "ultima_execucao": config["ultima_execucao"],
                "max_backups": config["max_backups"],
                "incluir_logs": config["incluir_logs"]
            },
            "backups": backups
        })
    
    @app.route('/manutencao/backup/criar', methods=['POST'])
    def criar_backup():
        sistema_backup = SistemaBackup()
        
        descricao = request.json.get('descricao', 'Backup manual')
        
        caminho_backup = sistema_backup.criar_backup(descricao)
        
        if caminho_backup:
            return jsonify({
                "sucesso": True,
                "mensagem": "Backup criado com sucesso",
                "arquivo": os.path.basename(caminho_backup)
            })
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Falha ao criar backup"
            })
    
    @app.route('/manutencao/backup/restaurar', methods=['POST'])
    def restaurar_backup():
        sistema_backup = SistemaBackup()
        
        arquivo = request.json.get('arquivo')
        
        if not arquivo:
            return jsonify({
                "sucesso": False,
                "mensagem": "Arquivo de backup não especificado"
            })
        
        caminho_backup = os.path.join(sistema_backup.diretorio_backup, arquivo)
        
        resultado = sistema_backup.restaurar_backup(caminho_backup)
        
        return jsonify({
            "sucesso": resultado,
            "mensagem": "Backup restaurado com sucesso" if resultado else "Falha ao restaurar backup"
        })
    
    @app.route('/manutencao/backup/download/<arquivo>')
    def download_backup(arquivo):
        sistema_backup = SistemaBackup()
        
        caminho_backup = os.path.join(sistema_backup.diretorio_backup, arquivo)
        
        if not os.path.exists(caminho_backup):
            return jsonify({
                "sucesso": False,
                "mensagem": "Arquivo de backup não encontrado"
            })
        
        return send_file(caminho_backup, as_attachment=True)
    
    @app.route('/manutencao/backup/configuracoes', methods=['POST'])
    def atualizar_configuracoes_backup():
        try:
            sistema_backup = SistemaBackup()
            
            # Carregar configuração atual
            with open(sistema_backup.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "backup_automatico" in dados:
                config["backup_automatico"] = dados["backup_automatico"]
            
            if "intervalo_dias" in dados:
                config["intervalo_dias"] = dados["intervalo_dias"]
            
            if "max_backups" in dados:
                config["max_backups"] = dados["max_backups"]
            
            if "incluir_logs" in dados:
                config["incluir_logs"] = dados["incluir_logs"]
            
            # Salvar configuração
            with open(sistema_backup.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            return jsonify({
                "sucesso": True,
                "mensagem": "Configurações atualizadas com sucesso"
            })
        except Exception as e:
            return jsonify({
                "sucesso": False,
                "mensagem": f"Erro ao atualizar configurações: {str(e)}"
            })
