"""
Módulo de Verificação de Integridade

Este módulo implementa um sistema de verificação de integridade para o software de ecocardiograma.
Permite verificar a integridade dos arquivos do sistema e do banco de dados.
"""

import os
import json
import sqlite3
import logging
import hashlib
import time
import datetime
import threading
import traceback
import shutil

# Configuração do logger
logger = logging.getLogger('sistema_integridade')

class SistemaIntegridade:
    def __init__(self):
        """
        Inicializa o sistema de verificação de integridade.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_integridade = os.path.join(self.diretorio_base, "integridade")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "integridade.json")
        self.arquivo_db = os.path.join(self.diretorio_base, "ecocardiograma.db")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_integridade, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de integridade."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "integridade.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de integridade."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "verificacao_automatica": True,
                "intervalo_dias": 7,
                "ultima_verificacao": None,
                "arquivos_essenciais": [
                    "src/main.py",
                    "src/integracao_modelos.py",
                    "ecocardiograma.db"
                ],
                "diretorios_essenciais": [
                    "src/modelos_laudo",
                    "src/static",
                    "src/templates"
                ],
                "assinaturas": {}
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de integridade criado")
    
    def gerar_assinaturas(self):
        """
        Gera assinaturas (hashes) para os arquivos essenciais do sistema.
        
        Returns:
            dict: Assinaturas dos arquivos
        """
        logger.info("Gerando assinaturas dos arquivos essenciais...")
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            assinaturas = {}
            
            # Gerar assinaturas para arquivos essenciais
            for arquivo_rel in config["arquivos_essenciais"]:
                arquivo = os.path.join(self.diretorio_base, arquivo_rel)
                
                if os.path.exists(arquivo) and os.path.isfile(arquivo):
                    # Calcular hash SHA-256
                    sha256 = hashlib.sha256()
                    
                    with open(arquivo, 'rb') as f:
                        for bloco in iter(lambda: f.read(4096), b''):
                            sha256.update(bloco)
                    
                    assinaturas[arquivo_rel] = {
                        "hash": sha256.hexdigest(),
                        "tamanho": os.path.getsize(arquivo),
                        "data_modificacao": datetime.datetime.fromtimestamp(os.path.getmtime(arquivo)).isoformat()
                    }
                else:
                    logger.warning(f"Arquivo essencial não encontrado: {arquivo}")
            
            # Atualizar configuração
            config["assinaturas"] = assinaturas
            config["ultima_verificacao"] = datetime.datetime.now().isoformat()
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Assinaturas geradas para {len(assinaturas)} arquivos")
            return assinaturas
            
        except Exception as e:
            logger.error(f"Erro ao gerar assinaturas: {str(e)}")
            return {}
    
    def verificar_integridade(self):
        """
        Verifica a integridade dos arquivos do sistema.
        
        Returns:
            dict: Resultado da verificação
        """
        logger.info("Verificando integridade do sistema...")
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            resultado = {
                "status": "OK",
                "arquivos_verificados": 0,
                "arquivos_modificados": [],
                "arquivos_faltando": [],
                "diretorios_faltando": [],
                "banco_dados": None,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Verificar arquivos essenciais
            for arquivo_rel, assinatura in config["assinaturas"].items():
                arquivo = os.path.join(self.diretorio_base, arquivo_rel)
                
                if not os.path.exists(arquivo) or not os.path.isfile(arquivo):
                    resultado["arquivos_faltando"].append(arquivo_rel)
                    resultado["status"] = "Erro"
                    continue
                
                # Calcular hash atual
                sha256 = hashlib.sha256()
                
                with open(arquivo, 'rb') as f:
                    for bloco in iter(lambda: f.read(4096), b''):
                        sha256.update(bloco)
                
                hash_atual = sha256.hexdigest()
                
                # Verificar se o hash mudou
                if hash_atual != assinatura["hash"]:
                    resultado["arquivos_modificados"].append({
                        "arquivo": arquivo_rel,
                        "hash_original": assinatura["hash"],
                        "hash_atual": hash_atual,
                        "data_modificacao": datetime.datetime.fromtimestamp(os.path.getmtime(arquivo)).isoformat()
                    })
                    
                    # Arquivos críticos modificados são erro, outros são aviso
                    if arquivo_rel in ["src/main.py", "src/integracao_modelos.py"]:
                        resultado["status"] = "Erro"
                    elif resultado["status"] == "OK":
                        resultado["status"] = "Aviso"
                
                resultado["arquivos_verificados"] += 1
            
            # Verificar diretórios essenciais
            for diretorio_rel in config["diretorios_essenciais"]:
                diretorio = os.path.join(self.diretorio_base, diretorio_rel)
                
                if not os.path.exists(diretorio) or not os.path.isdir(diretorio):
                    resultado["diretorios_faltando"].append(diretorio_rel)
                    resultado["status"] = "Erro"
                    continue
                
                # Verificar se o diretório não está vazio
                if len(os.listdir(diretorio)) == 0:
                    resultado["diretorios_faltando"].append(f"{diretorio_rel} (vazio)")
                    
                    # Diretórios vazios são aviso, não erro
                    if resultado["status"] == "OK":
                        resultado["status"] = "Aviso"
            
            # Verificar banco de dados
            resultado["banco_dados"] = self.verificar_integridade_banco_dados()
            
            if resultado["banco_dados"]["status"] != "OK":
                resultado["status"] = "Erro"
            
            # Salvar resultado
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"verificacao_integridade_{timestamp}.json"
            caminho_arquivo = os.path.join(self.diretorio_integridade, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=4)
            
            # Atualizar data da última verificação
            config["ultima_verificacao"] = datetime.datetime.now().isoformat()
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Verificação de integridade concluída: {resultado['status']}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {str(e)}")
            return {
                "status": "Erro",
                "mensagem": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def verificar_integridade_banco_dados(self):
        """
        Verifica a integridade do banco de dados.
        
        Returns:
            dict: Resultado da verificação
        """
        try:
            if not os.path.exists(self.arquivo_db):
                return {
                    "status": "Erro",
                    "mensagem": "Banco de dados não encontrado"
                }
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar integridade
            cursor.execute("PRAGMA integrity_check")
            integridade = cursor.fetchone()[0]
            
            # Verificar consistência
            cursor.execute("PRAGMA foreign_key_check")
            consistencia = cursor.fetchall()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
            
            # Tabelas essenciais
            tabelas_essenciais = ["exames", "parametros", "laudos", "modelos_laudo", "medicos"]
            tabelas_faltando = [tabela for tabela in tabelas_essenciais if tabela not in tabelas]
            
            conn.close()
            
            resultado = {
                "status": "OK" if integridade == "ok" and not consistencia and not tabelas_faltando else "Erro",
                "integridade": integridade,
                "consistencia": "OK" if not consistencia else "Erro",
                "tabelas_encontradas": tabelas,
                "tabelas_faltando": tabelas_faltando,
                "tamanho_mb": round(os.path.getsize(self.arquivo_db) / (1024 * 1024), 2)
            }
            
            if consistencia:
                resultado["detalhes_consistencia"] = consistencia
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade do banco de dados: {str(e)}")
            return {
                "status": "Erro",
                "mensagem": str(e)
            }
    
    def reparar_banco_dados(self):
        """
        Tenta reparar o banco de dados.
        
        Returns:
            dict: Resultado da reparação
        """
        logger.info("Tentando reparar banco de dados...")
        
        try:
            if not os.path.exists(self.arquivo_db):
                return {
                    "sucesso": False,
                    "mensagem": "Banco de dados não encontrado"
                }
            
            # Criar backup antes de reparar
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.diretorio_integridade, f"backup_db_{timestamp}.db")
            
            shutil.copy2(self.arquivo_db, backup_path)
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Executar vacuum para reconstruir o banco de dados
            cursor.execute("VACUUM")
            
            # Verificar integridade após reparação
            cursor.execute("PRAGMA integrity_check")
            integridade = cursor.fetchone()[0]
            
            conn.close()
            
            if integridade == "ok":
                logger.info("Banco de dados reparado com sucesso")
                return {
                    "sucesso": True,
                    "mensagem": "Banco de dados reparado com sucesso",
                    "backup": backup_path
                }
            else:
                logger.error(f"Falha ao reparar banco de dados: {integridade}")
                
                # Restaurar backup
                shutil.copy2(backup_path, self.arquivo_db)
                
                return {
                    "sucesso": False,
                    "mensagem": f"Falha ao reparar banco de dados: {integridade}",
                    "backup": backup_path
                }
            
        except Exception as e:
            logger.error(f"Erro ao reparar banco de dados: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": str(e)
            }
    
    def restaurar_arquivo_original(self, arquivo_rel):
        """
        Restaura um arquivo para sua versão original a partir do backup.
        
        Args:
            arquivo_rel: Caminho relativo do arquivo
            
        Returns:
            dict: Resultado da restauração
        """
        logger.info(f"Tentando restaurar arquivo original: {arquivo_rel}")
        
        try:
            # Verificar se existe um backup do arquivo
            from manutencao.backup import SistemaBackup
            
            sistema_backup = SistemaBackup()
            backups = sistema_backup.listar_backups()
            
            if not backups:
                return {
                    "sucesso": False,
                    "mensagem": "Nenhum backup encontrado"
                }
            
            # Usar o backup mais recente
            backup_mais_recente = backups[-1]
            caminho_backup = os.path.join(sistema_backup.diretorio_backup, backup_mais_recente["arquivo"])
            
            # Extrair arquivo do backup
            import tempfile
            import zipfile
            
            diretorio_temp = tempfile.mkdtemp()
            
            with zipfile.ZipFile(caminho_backup, 'r') as zip_ref:
                # Extrair apenas o arquivo desejado
                for item in zip_ref.namelist():
                    if item == arquivo_rel:
                        zip_ref.extract(item, diretorio_temp)
                        break
            
            arquivo_backup = os.path.join(diretorio_temp, arquivo_rel)
            arquivo_destino = os.path.join(self.diretorio_base, arquivo_rel)
            
            if not os.path.exists(arquivo_backup):
                shutil.rmtree(diretorio_temp)
                return {
                    "sucesso": False,
                    "mensagem": f"Arquivo {arquivo_rel} não encontrado no backup"
                }
            
            # Criar backup do arquivo atual antes de substituir
            if os.path.exists(arquivo_destino):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_atual = f"{arquivo_destino}.bak_{timestamp}"
                shutil.copy2(arquivo_destino, backup_atual)
            
            # Garantir que o diretório de destino existe
            os.makedirs(os.path.dirname(arquivo_destino), exist_ok=True)
            
            # Copiar arquivo do backup
            shutil.copy2(arquivo_backup, arquivo_destino)
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            logger.info(f"Arquivo {arquivo_rel} restaurado com sucesso")
            return {
                "sucesso": True,
                "mensagem": f"Arquivo {arquivo_rel} restaurado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao restaurar arquivo original: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": str(e)
            }
    
    def verificar_automaticamente(self):
        """
        Verifica se é necessário realizar uma verificação automática de integridade.
        
        Returns:
            bool: True se uma verificação automática foi realizada, False caso contrário
        """
        try:
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar se a verificação automática está ativada
            if not config.get("verificacao_automatica", True):
                return False
            
            # Verificar a data da última verificação
            ultima_verificacao = config.get("ultima_verificacao")
            if not ultima_verificacao:
                # Nunca foi feita uma verificação, fazer agora
                self.verificar_integridade()
                return True
            
            # Converter para datetime
            ultima_data = datetime.datetime.fromisoformat(ultima_verificacao)
            agora = datetime.datetime.now()
            
            # Calcular diferença em dias
            diferenca_dias = (agora - ultima_data).days
            
            # Verificar se passou o intervalo configurado
            if diferenca_dias >= config.get("intervalo_dias", 7):
                self.verificar_integridade()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar automaticamente: {str(e)}")
            return False

# Função para integração com a aplicação principal
def verificar_integridade_ao_iniciar(app):
    """
    Função para verificar integridade ao iniciar a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.before_first_request
    def verificar_integridade():
        try:
            sistema_integridade = SistemaIntegridade()
            sistema_integridade.verificar_automaticamente()
        except Exception as e:
            # Registrar erro, mas não interromper a inicialização
            print(f"Erro ao verificar integridade: {str(e)}")

# Adicionar rotas para o sistema de integridade
def adicionar_rotas_integridade(app):
    """
    Adiciona rotas para o sistema de integridade à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify
    
    @app.route('/manutencao/integridade')
    def pagina_integridade():
        sistema_integridade = SistemaIntegridade()
        
        # Carregar configuração
        with open(sistema_integridade.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({
            "configuracoes": {
                "verificacao_automatica": config["verificacao_automatica"],
                "intervalo_dias": config["intervalo_dias"],
                "ultima_verificacao": config["ultima_verificacao"]
            },
            "arquivos_essenciais": config["arquivos_essenciais"],
            "diretorios_essenciais": config["diretorios_essenciais"]
        })
    
    @app.route('/manutencao/integridade/verificar', methods=['POST'])
    def verificar_integridade():
        sistema_integridade = SistemaIntegridade()
        
        resultado = sistema_integridade.verificar_integridade()
        
        return jsonify(resultado)
    
    @app.route('/manutencao/integridade/gerar_assinaturas', methods=['POST'])
    def gerar_assinaturas():
        sistema_integridade = SistemaIntegridade()
        
        assinaturas = sistema_integridade.gerar_assinaturas()
        
        return jsonify({
            "sucesso": bool(assinaturas),
            "mensagem": f"Assinaturas geradas para {len(assinaturas)} arquivos" if assinaturas else "Falha ao gerar assinaturas",
            "assinaturas": assinaturas
        })
    
    @app.route('/manutencao/integridade/reparar_banco', methods=['POST'])
    def reparar_banco():
        sistema_integridade = SistemaIntegridade()
        
        resultado = sistema_integridade.reparar_banco_dados()
        
        return jsonify(resultado)
    
    @app.route('/manutencao/integridade/restaurar_arquivo', methods=['POST'])
    def restaurar_arquivo():
        sistema_integridade = SistemaIntegridade()
        
        arquivo = request.json.get('arquivo')
        
        if not arquivo:
            return jsonify({
                "sucesso": False,
                "mensagem": "Arquivo não especificado"
            })
        
        resultado = sistema_integridade.restaurar_arquivo_original(arquivo)
        
        return jsonify(resultado)
    
    @app.route('/manutencao/integridade/configuracoes', methods=['POST'])
    def atualizar_configuracoes_integridade():
        try:
            sistema_integridade = SistemaIntegridade()
            
            # Carregar configuração atual
            with open(sistema_integridade.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "verificacao_automatica" in dados:
                config["verificacao_automatica"] = dados["verificacao_automatica"]
            
            if "intervalo_dias" in dados:
                config["intervalo_dias"] = dados["intervalo_dias"]
            
            if "arquivos_essenciais" in dados:
                config["arquivos_essenciais"] = dados["arquivos_essenciais"]
            
            if "diretorios_essenciais" in dados:
                config["diretorios_essenciais"] = dados["diretorios_essenciais"]
            
            # Salvar configuração
            with open(sistema_integridade.arquivo_config, 'w', encoding='utf-8') as f:
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
