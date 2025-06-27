"""
Módulo de Sistema de Logs

Este módulo implementa um sistema de logs centralizado para o software de ecocardiograma.
Permite registrar, visualizar e gerenciar logs de todas as operações do sistema.
"""

import os
import json
import logging
import logging.handlers
import time
import datetime
import sqlite3
import traceback
import sys
from flask import request, session

# Configuração do logger principal
logger = logging.getLogger('sistema_logs')

class SistemaLogs:
    def __init__(self):
        """
        Inicializa o sistema de logs centralizado.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_logs = os.path.join(self.diretorio_base, "logs")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "logs.json")
        self.arquivo_db_logs = os.path.join(self.diretorio_logs, "sistema_logs.db")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_logs, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Inicializar banco de dados de logs
        self._inicializar_db()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs principal."""
        # Carregar configuração
        with open(self.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Configurar logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config["nivel_log"].upper()))
        
        # Remover handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Adicionar handler para arquivo
        log_file = os.path.join(self.diretorio_logs, "sistema.log")
        
        # Usar RotatingFileHandler para limitar tamanho dos arquivos
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=config["tamanho_max_arquivo"] * 1024 * 1024,  # Converter para bytes
            backupCount=config["max_arquivos_backup"]
        )
        
        # Configurar formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
        
        # Adicionar handler para console se estiver em modo de desenvolvimento
        if config.get("log_console", False):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Configurar logger específico do sistema de logs
        logger.setLevel(logging.INFO)
        
        # Adicionar handler para banco de dados
        db_handler = DatabaseLogHandler(self.arquivo_db_logs)
        db_handler.setLevel(logging.INFO)
        logger.addHandler(db_handler)
        
        logger.info("Sistema de logs inicializado")
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de logs."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "nivel_log": "INFO",
                "tamanho_max_arquivo": 10,  # MB
                "max_arquivos_backup": 5,
                "log_console": False,
                "log_acesso": True,
                "log_banco_dados": True,
                "retencao_logs_dias": 90
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            print("Arquivo de configuração de logs criado")
    
    def _inicializar_db(self):
        """Inicializa o banco de dados para armazenamento de logs."""
        conn = sqlite3.connect(self.arquivo_db_logs)
        cursor = conn.cursor()
        
        # Criar tabela de logs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            nivel TEXT NOT NULL,
            origem TEXT,
            mensagem TEXT NOT NULL,
            usuario TEXT,
            ip TEXT,
            detalhes TEXT
        )
        ''')
        
        # Criar índice para melhorar performance de consultas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_nivel ON logs (nivel)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_origem ON logs (origem)')
        
        conn.commit()
        conn.close()
    
    def registrar_log(self, nivel, mensagem, origem=None, usuario=None, ip=None, detalhes=None):
        """
        Registra uma entrada de log no banco de dados.
        
        Args:
            nivel: Nível do log (INFO, WARNING, ERROR, CRITICAL)
            mensagem: Mensagem do log
            origem: Origem do log (módulo ou componente)
            usuario: Usuário que realizou a ação
            ip: Endereço IP do usuário
            detalhes: Detalhes adicionais (como traceback)
        """
        try:
            conn = sqlite3.connect(self.arquivo_db_logs)
            cursor = conn.cursor()
            
            timestamp = datetime.datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO logs (timestamp, nivel, origem, mensagem, usuario, ip, detalhes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, nivel, origem, mensagem, usuario, ip, detalhes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao registrar log: {str(e)}")
    
    def buscar_logs(self, nivel=None, origem=None, data_inicio=None, data_fim=None, usuario=None, limite=100):
        """
        Busca logs no banco de dados.
        
        Args:
            nivel: Filtrar por nível (INFO, WARNING, ERROR, CRITICAL)
            origem: Filtrar por origem
            data_inicio: Data de início (formato ISO)
            data_fim: Data de fim (formato ISO)
            usuario: Filtrar por usuário
            limite: Limite de resultados
            
        Returns:
            list: Lista de logs
        """
        try:
            conn = sqlite3.connect(self.arquivo_db_logs)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Construir consulta
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if nivel:
                query += " AND nivel = ?"
                params.append(nivel)
            
            if origem:
                query += " AND origem LIKE ?"
                params.append(f"%{origem}%")
            
            if data_inicio:
                query += " AND timestamp >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND timestamp <= ?"
                params.append(data_fim)
            
            if usuario:
                query += " AND usuario LIKE ?"
                params.append(f"%{usuario}%")
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limite)
            
            cursor.execute(query, params)
            
            # Converter para lista de dicionários
            resultado = []
            for row in cursor.fetchall():
                resultado.append(dict(row))
            
            conn.close()
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao buscar logs: {str(e)}")
            return []
    
    def limpar_logs_antigos(self):
        """
        Remove logs antigos com base na configuração de retenção.
        
        Returns:
            int: Número de logs removidos
        """
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            retencao_dias = config.get("retencao_logs_dias", 90)
            
            # Calcular data limite
            data_limite = (datetime.datetime.now() - datetime.timedelta(days=retencao_dias)).isoformat()
            
            conn = sqlite3.connect(self.arquivo_db_logs)
            cursor = conn.cursor()
            
            # Contar registros a serem removidos
            cursor.execute("SELECT COUNT(*) FROM logs WHERE timestamp < ?", (data_limite,))
            count = cursor.fetchone()[0]
            
            # Remover registros antigos
            cursor.execute("DELETE FROM logs WHERE timestamp < ?", (data_limite,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Limpeza de logs: {count} registros removidos")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao limpar logs antigos: {str(e)}")
            return 0
    
    def exportar_logs(self, formato="json", filtros=None):
        """
        Exporta logs para um arquivo.
        
        Args:
            formato: Formato de exportação (json, csv)
            filtros: Filtros para a busca de logs
            
        Returns:
            str: Caminho para o arquivo exportado ou None em caso de erro
        """
        try:
            # Aplicar filtros padrão se não especificados
            if filtros is None:
                filtros = {}
            
            # Buscar logs
            logs = self.buscar_logs(
                nivel=filtros.get("nivel"),
                origem=filtros.get("origem"),
                data_inicio=filtros.get("data_inicio"),
                data_fim=filtros.get("data_fim"),
                usuario=filtros.get("usuario"),
                limite=filtros.get("limite", 1000)
            )
            
            if not logs:
                logger.warning("Nenhum log encontrado para exportação")
                return None
            
            # Criar nome do arquivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"logs_export_{timestamp}.{formato}"
            caminho_arquivo = os.path.join(self.diretorio_logs, nome_arquivo)
            
            # Exportar no formato especificado
            if formato == "json":
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=4)
            
            elif formato == "csv":
                import csv
                
                with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Escrever cabeçalho
                    if logs:
                        writer.writerow(logs[0].keys())
                    
                    # Escrever dados
                    for log in logs:
                        writer.writerow(log.values())
            
            else:
                logger.error(f"Formato de exportação não suportado: {formato}")
                return None
            
            logger.info(f"Logs exportados para {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao exportar logs: {str(e)}")
            return None


class DatabaseLogHandler(logging.Handler):
    """Handler personalizado para salvar logs no banco de dados."""
    
    def __init__(self, db_path):
        """
        Inicializa o handler.
        
        Args:
            db_path: Caminho para o banco de dados de logs
        """
        super().__init__()
        self.db_path = db_path
    
    def emit(self, record):
        """
        Salva o registro de log no banco de dados.
        
        Args:
            record: Registro de log
        """
        try:
            # Extrair informações do registro
            timestamp = datetime.datetime.fromtimestamp(record.created).isoformat()
            nivel = record.levelname
            origem = record.name
            mensagem = self.format(record)
            
            # Extrair informações de exceção se disponível
            detalhes = None
            if record.exc_info:
                detalhes = ''.join(traceback.format_exception(*record.exc_info))
            
            # Extrair informações de usuário e IP se disponível
            usuario = None
            ip = None
            
            # Conectar ao banco de dados e inserir log
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO logs (timestamp, nivel, origem, mensagem, usuario, ip, detalhes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, nivel, origem, mensagem, usuario, ip, detalhes))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Não podemos usar logging aqui para evitar recursão infinita
            print(f"Erro ao salvar log no banco de dados: {str(e)}")


# Função para integração com a aplicação principal
def configurar_logs_aplicacao(app):
    """
    Configura o sistema de logs para a aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    sistema_logs = SistemaLogs()
    
    # Carregar configuração
    with open(sistema_logs.arquivo_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Configurar logger da aplicação Flask
    app.logger.setLevel(getattr(logging, config["nivel_log"].upper()))
    
    # Adicionar handler para banco de dados
    db_handler = DatabaseLogHandler(sistema_logs.arquivo_db_logs)
    db_handler.setLevel(logging.INFO)
    app.logger.addHandler(db_handler)
    
    # Registrar logs de acesso
    if config.get("log_acesso", True):
        @app.before_request
        def log_request_info():
            # Ignorar requisições para arquivos estáticos
            if request.path.startswith('/static/'):
                return
            
            # Registrar acesso
            usuario = session.get('usuario', 'anônimo') if hasattr(session, 'usuario') else 'anônimo'
            
            sistema_logs.registrar_log(
                nivel="INFO",
                mensagem=f"Acesso: {request.method} {request.path}",
                origem="flask.acesso",
                usuario=usuario,
                ip=request.remote_addr,
                detalhes=json.dumps({
                    "user_agent": request.user_agent.string,
                    "args": dict(request.args),
                    "form": dict(request.form) if request.method == 'POST' else None
                })
            )
    
    # Registrar erros
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Registrar erro
        tb = traceback.format_exc()
        
        sistema_logs.registrar_log(
            nivel="ERROR",
            mensagem=f"Erro não tratado: {str(e)}",
            origem="flask.erro",
            usuario=session.get('usuario', 'anônimo') if hasattr(session, 'usuario') else 'anônimo',
            ip=request.remote_addr if request else None,
            detalhes=tb
        )
        
        # Continuar com o tratamento padrão de erros
        return app.handle_exception(e)
    
    # Configurar limpeza periódica de logs
    @app.before_first_request
    def configurar_limpeza_logs():
        sistema_logs.limpar_logs_antigos()

# Adicionar rotas para o sistema de logs
def adicionar_rotas_logs(app):
    """
    Adiciona rotas para o sistema de logs à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify, send_file
    
    @app.route('/manutencao/logs')
    def pagina_logs():
        sistema_logs = SistemaLogs()
        
        # Carregar configuração
        with open(sistema_logs.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Parâmetros de busca
        nivel = request.args.get('nivel')
        origem = request.args.get('origem')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        usuario = request.args.get('usuario')
        limite = int(request.args.get('limite', 100))
        
        # Buscar logs
        logs = sistema_logs.buscar_logs(
            nivel=nivel,
            origem=origem,
            data_inicio=data_inicio,
            data_fim=data_fim,
            usuario=usuario,
            limite=limite
        )
        
        return jsonify({
            "configuracoes": {
                "nivel_log": config["nivel_log"],
                "tamanho_max_arquivo": config["tamanho_max_arquivo"],
                "max_arquivos_backup": config["max_arquivos_backup"],
                "log_console": config["log_console"],
                "log_acesso": config["log_acesso"],
                "log_banco_dados": config["log_banco_dados"],
                "retencao_logs_dias": config["retencao_logs_dias"]
            },
            "logs": logs
        })
    
    @app.route('/manutencao/logs/exportar', methods=['POST'])
    def exportar_logs():
        sistema_logs = SistemaLogs()
        
        formato = request.json.get('formato', 'json')
        filtros = request.json.get('filtros', {})
        
        caminho_arquivo = sistema_logs.exportar_logs(formato, filtros)
        
        if caminho_arquivo:
            return jsonify({
                "sucesso": True,
                "mensagem": "Logs exportados com sucesso",
                "arquivo": os.path.basename(caminho_arquivo)
            })
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": "Falha ao exportar logs"
            })
    
    @app.route('/manutencao/logs/download/<arquivo>')
    def download_logs(arquivo):
        sistema_logs = SistemaLogs()
        
        caminho_arquivo = os.path.join(sistema_logs.diretorio_logs, arquivo)
        
        if not os.path.exists(caminho_arquivo):
            return jsonify({
                "sucesso": False,
                "mensagem": "Arquivo não encontrado"
            })
        
        return send_file(caminho_arquivo, as_attachment=True)
    
    @app.route('/manutencao/logs/limpar', methods=['POST'])
    def limpar_logs():
        sistema_logs = SistemaLogs()
        
        count = sistema_logs.limpar_logs_antigos()
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"{count} logs antigos removidos"
        })
    
    @app.route('/manutencao/logs/configuracoes', methods=['POST'])
    def atualizar_configuracoes_logs():
        try:
            sistema_logs = SistemaLogs()
            
            # Carregar configuração atual
            with open(sistema_logs.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "nivel_log" in dados:
                config["nivel_log"] = dados["nivel_log"]
            
            if "tamanho_max_arquivo" in dados:
                config["tamanho_max_arquivo"] = dados["tamanho_max_arquivo"]
            
            if "max_arquivos_backup" in dados:
                config["max_arquivos_backup"] = dados["max_arquivos_backup"]
            
            if "log_console" in dados:
                config["log_console"] = dados["log_console"]
            
            if "log_acesso" in dados:
                config["log_acesso"] = dados["log_acesso"]
            
            if "log_banco_dados" in dados:
                config["log_banco_dados"] = dados["log_banco_dados"]
            
            if "retencao_logs_dias" in dados:
                config["retencao_logs_dias"] = dados["retencao_logs_dias"]
            
            # Salvar configuração
            with open(sistema_logs.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # Reconfigurar logger
            sistema_logs._configurar_logger()
            
            return jsonify({
                "sucesso": True,
                "mensagem": "Configurações atualizadas com sucesso"
            })
        except Exception as e:
            return jsonify({
                "sucesso": False,
                "mensagem": f"Erro ao atualizar configurações: {str(e)}"
            })
