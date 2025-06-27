"""
Módulo de Atualização Automática

Este módulo implementa um sistema de atualização automática para o software de ecocardiograma.
Permite verificar, baixar e instalar atualizações de forma segura sem comprometer os dados existentes.
"""

import os
import json
import sqlite3
import requests
import hashlib
import shutil
import sys
import logging
from datetime import datetime
import subprocess
import zipfile
import tempfile

# Configuração do logger
logger = logging.getLogger('sistema_atualizacao')

class SistemaAtualizacao:
    def __init__(self, versao_atual="1.0.0", url_servidor="https://atualizacoes.ecocardiograma.com.br"):
        """
        Inicializa o sistema de atualização.
        
        Args:
            versao_atual: Versão atual do software
            url_servidor: URL do servidor de atualizações
        """
        self.versao_atual = versao_atual
        self.url_servidor = url_servidor
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_backup = os.path.join(self.diretorio_base, "backups", "atualizacoes")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "atualizacao.json")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_backup, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de atualização."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "atualizacao.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de atualização."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "versao_atual": self.versao_atual,
                "ultima_verificacao": None,
                "atualizacao_automatica": True,
                "verificar_ao_iniciar": True,
                "canal": "estavel",
                "historico_atualizacoes": []
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de atualização criado")
        else:
            # Carregar configuração existente
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar a versão atual se necessário
            if config["versao_atual"] != self.versao_atual:
                config["versao_atual"] = self.versao_atual
                with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                
                logger.info(f"Versão atual atualizada para {self.versao_atual}")
    
    def verificar_atualizacoes(self):
        """
        Verifica se há atualizações disponíveis.
        
        Returns:
            dict: Informações sobre a atualização disponível ou None se não houver
        """
        logger.info("Verificando atualizações...")
        
        try:
            # Em um ambiente real, isso faria uma requisição HTTP
            # Simulação para desenvolvimento
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar data da última verificação
            config["ultima_verificacao"] = datetime.now().isoformat()
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # Simular verificação de versão
            versao_atual = tuple(map(int, self.versao_atual.split('.')))
            versao_disponivel = (1, 0, 1)  # Simulação
            
            if versao_disponivel > versao_atual:
                logger.info(f"Nova versão disponível: {'.'.join(map(str, versao_disponivel))}")
                return {
                    "versao": '.'.join(map(str, versao_disponivel)),
                    "url_download": f"{self.url_servidor}/downloads/eco_v{'_'.join(map(str, versao_disponivel))}.zip",
                    "notas_versao": "Melhorias de desempenho e correções de bugs",
                    "tamanho_mb": 15.2,
                    "obrigatoria": False
                }
            else:
                logger.info("Nenhuma atualização disponível")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {str(e)}")
            return None
    
    def baixar_atualizacao(self, info_atualizacao):
        """
        Baixa a atualização disponível.
        
        Args:
            info_atualizacao: Informações sobre a atualização
            
        Returns:
            str: Caminho para o arquivo baixado ou None em caso de erro
        """
        logger.info(f"Baixando atualização versão {info_atualizacao['versao']}...")
        
        try:
            # Em um ambiente real, isso baixaria o arquivo
            # Simulação para desenvolvimento
            arquivo_temp = os.path.join(tempfile.gettempdir(), f"eco_update_{info_atualizacao['versao']}.zip")
            
            # Simular download
            with open(arquivo_temp, 'wb') as f:
                f.write(b'Conteudo simulado da atualizacao')
            
            logger.info(f"Atualização baixada para {arquivo_temp}")
            return arquivo_temp
            
        except Exception as e:
            logger.error(f"Erro ao baixar atualização: {str(e)}")
            return None
    
    def verificar_integridade(self, arquivo_atualizacao, hash_esperado=None):
        """
        Verifica a integridade do arquivo de atualização.
        
        Args:
            arquivo_atualizacao: Caminho para o arquivo de atualização
            hash_esperado: Hash SHA-256 esperado para o arquivo
            
        Returns:
            bool: True se a integridade for verificada, False caso contrário
        """
        logger.info(f"Verificando integridade do arquivo {arquivo_atualizacao}...")
        
        try:
            # Calcular hash do arquivo
            sha256 = hashlib.sha256()
            with open(arquivo_atualizacao, 'rb') as f:
                for bloco in iter(lambda: f.read(4096), b''):
                    sha256.update(bloco)
            
            hash_calculado = sha256.hexdigest()
            
            # Se não houver hash esperado, apenas retornar True (para desenvolvimento)
            if not hash_esperado:
                logger.info("Hash não fornecido, pulando verificação de integridade")
                return True
            
            # Verificar se o hash corresponde
            if hash_calculado == hash_esperado:
                logger.info("Verificação de integridade bem-sucedida")
                return True
            else:
                logger.error(f"Falha na verificação de integridade. Esperado: {hash_esperado}, Calculado: {hash_calculado}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar integridade: {str(e)}")
            return False
    
    def criar_backup_pre_atualizacao(self):
        """
        Cria um backup do sistema antes da atualização.
        
        Returns:
            str: Caminho para o backup ou None em caso de erro
        """
        logger.info("Criando backup pré-atualização...")
        
        try:
            # Criar nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backup_pre_atualizacao_{self.versao_atual}_{timestamp}.zip"
            caminho_backup = os.path.join(self.diretorio_backup, nome_backup)
            
            # Criar arquivo ZIP com o conteúdo do diretório
            with zipfile.ZipFile(caminho_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.diretorio_base):
                    # Ignorar diretórios de backup e logs
                    if "backups" in root or "logs" in root:
                        continue
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.diretorio_base)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Backup criado em {caminho_backup}")
            return caminho_backup
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None
    
    def instalar_atualizacao(self, arquivo_atualizacao):
        """
        Instala a atualização baixada.
        
        Args:
            arquivo_atualizacao: Caminho para o arquivo de atualização
            
        Returns:
            bool: True se a instalação for bem-sucedida, False caso contrário
        """
        logger.info(f"Instalando atualização de {arquivo_atualizacao}...")
        
        # Criar backup antes da atualização
        backup = self.criar_backup_pre_atualizacao()
        if not backup:
            logger.error("Falha ao criar backup, abortando atualização")
            return False
        
        try:
            # Extrair arquivo de atualização para diretório temporário
            diretorio_temp = tempfile.mkdtemp()
            
            with zipfile.ZipFile(arquivo_atualizacao, 'r') as zip_ref:
                zip_ref.extractall(diretorio_temp)
            
            # Ler informações da atualização (versão, etc.)
            info_path = os.path.join(diretorio_temp, "update_info.json")
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    info_atualizacao = json.load(f)
                nova_versao = info_atualizacao.get("versao", "desconhecida")
            else:
                # Se não houver arquivo de informações, usar nome do arquivo
                nova_versao = os.path.basename(arquivo_atualizacao).split("_")[2].replace(".zip", "")
            
            # Copiar arquivos da atualização para o diretório do sistema
            for root, dirs, files in os.walk(diretorio_temp):
                # Ignorar arquivo de informações
                if "update_info.json" in files:
                    files.remove("update_info.json")
                
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, diretorio_temp)
                    dst_path = os.path.join(self.diretorio_base, rel_path)
                    
                    # Criar diretório de destino se não existir
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(src_path, dst_path)
            
            # Atualizar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar versão e histórico
            config["versao_atual"] = nova_versao
            config["historico_atualizacoes"].append({
                "data": datetime.now().isoformat(),
                "versao_anterior": self.versao_atual,
                "versao_nova": nova_versao,
                "backup": backup
            })
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            # Atualizar versão atual da instância
            self.versao_atual = nova_versao
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            logger.info(f"Atualização para versão {nova_versao} instalada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao instalar atualização: {str(e)}")
            
            # Tentar restaurar backup em caso de erro
            logger.info("Tentando restaurar backup...")
            try:
                self.restaurar_backup(backup)
                logger.info("Backup restaurado com sucesso")
            except Exception as restore_error:
                logger.error(f"Erro ao restaurar backup: {str(restore_error)}")
            
            return False
    
    def restaurar_backup(self, caminho_backup):
        """
        Restaura um backup anterior.
        
        Args:
            caminho_backup: Caminho para o arquivo de backup
            
        Returns:
            bool: True se a restauração for bem-sucedida, False caso contrário
        """
        logger.info(f"Restaurando backup de {caminho_backup}...")
        
        try:
            # Extrair backup para diretório temporário
            diretorio_temp = tempfile.mkdtemp()
            
            with zipfile.ZipFile(caminho_backup, 'r') as zip_ref:
                zip_ref.extractall(diretorio_temp)
            
            # Copiar arquivos do backup para o diretório do sistema
            for root, dirs, files in os.walk(diretorio_temp):
                for file in files:
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, diretorio_temp)
                    dst_path = os.path.join(self.diretorio_base, rel_path)
                    
                    # Criar diretório de destino se não existir
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(src_path, dst_path)
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            logger.info("Backup restaurado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return False
    
    def atualizar_automaticamente(self):
        """
        Executa o processo completo de atualização automática.
        
        Returns:
            bool: True se a atualização for bem-sucedida, False caso contrário
        """
        logger.info("Iniciando processo de atualização automática...")
        
        # Verificar se há atualizações
        info_atualizacao = self.verificar_atualizacoes()
        if not info_atualizacao:
            logger.info("Nenhuma atualização disponível")
            return False
        
        # Baixar atualização
        arquivo_atualizacao = self.baixar_atualizacao(info_atualizacao)
        if not arquivo_atualizacao:
            logger.error("Falha ao baixar atualização")
            return False
        
        # Verificar integridade
        if not self.verificar_integridade(arquivo_atualizacao):
            logger.error("Falha na verificação de integridade")
            return False
        
        # Instalar atualização
        resultado = self.instalar_atualizacao(arquivo_atualizacao)
        
        # Limpar arquivo temporário
        try:
            os.remove(arquivo_atualizacao)
        except:
            pass
        
        return resultado

# Função para integração com a aplicação principal
def verificar_atualizacoes_ao_iniciar(app):
    """
    Função para verificar atualizações ao iniciar a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.before_first_request
    def verificar_atualizacoes():
        try:
            # Carregar configuração
            diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            arquivo_config = os.path.join(diretorio_base, "config", "atualizacao.json")
            
            if os.path.exists(arquivo_config):
                with open(arquivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Verificar se a verificação automática está ativada
                if config.get("verificar_ao_iniciar", True):
                    sistema_atualizacao = SistemaAtualizacao(versao_atual=config.get("versao_atual", "1.0.0"))
                    info_atualizacao = sistema_atualizacao.verificar_atualizacoes()
                    
                    if info_atualizacao:
                        # Registrar informação sobre atualização disponível
                        app.config["ATUALIZACAO_DISPONIVEL"] = info_atualizacao
        except Exception as e:
            # Registrar erro, mas não interromper a inicialização
            print(f"Erro ao verificar atualizações: {str(e)}")

# Adicionar rotas para o sistema de atualização
def adicionar_rotas_atualizacao(app):
    """
    Adiciona rotas para o sistema de atualização à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.route('/manutencao/atualizacao')
    def pagina_atualizacao():
        sistema_atualizacao = SistemaAtualizacao()
        
        # Carregar configuração
        with open(sistema_atualizacao.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar atualizações
        info_atualizacao = sistema_atualizacao.verificar_atualizacoes()
        
        return {
            "versao_atual": config["versao_atual"],
            "ultima_verificacao": config["ultima_verificacao"],
            "atualizacao_disponivel": info_atualizacao,
            "configuracoes": {
                "atualizacao_automatica": config["atualizacao_automatica"],
                "verificar_ao_iniciar": config["verificar_ao_iniciar"],
                "canal": config["canal"]
            },
            "historico_atualizacoes": config["historico_atualizacoes"]
        }
    
    @app.route('/manutencao/atualizacao/verificar', methods=['POST'])
    def verificar_atualizacao():
        sistema_atualizacao = SistemaAtualizacao()
        info_atualizacao = sistema_atualizacao.verificar_atualizacoes()
        
        return {
            "sucesso": True,
            "atualizacao_disponivel": info_atualizacao is not None,
            "info_atualizacao": info_atualizacao
        }
    
    @app.route('/manutencao/atualizacao/atualizar', methods=['POST'])
    def executar_atualizacao():
        sistema_atualizacao = SistemaAtualizacao()
        resultado = sistema_atualizacao.atualizar_automaticamente()
        
        return {
            "sucesso": resultado,
            "mensagem": "Atualização concluída com sucesso" if resultado else "Falha na atualização"
        }
    
    @app.route('/manutencao/atualizacao/configuracoes', methods=['POST'])
    def atualizar_configuracoes():
        try:
            sistema_atualizacao = SistemaAtualizacao()
            
            # Carregar configuração atual
            with open(sistema_atualizacao.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "atualizacao_automatica" in dados:
                config["atualizacao_automatica"] = dados["atualizacao_automatica"]
            
            if "verificar_ao_iniciar" in dados:
                config["verificar_ao_iniciar"] = dados["verificar_ao_iniciar"]
            
            if "canal" in dados:
                config["canal"] = dados["canal"]
            
            # Salvar configuração
            with open(sistema_atualizacao.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            return {
                "sucesso": True,
                "mensagem": "Configurações atualizadas com sucesso"
            }
        except Exception as e:
            return {
                "sucesso": False,
                "mensagem": f"Erro ao atualizar configurações: {str(e)}"
            }
