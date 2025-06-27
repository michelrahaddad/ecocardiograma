"""
Módulo de Limpeza de Arquivos Temporários

Este módulo implementa um sistema de limpeza de arquivos temporários para o software de ecocardiograma.
Permite identificar e remover arquivos temporários e caches desnecessários.
"""

import os
import json
import logging
import time
import datetime
import shutil
import re
import traceback

# Configuração do logger
logger = logging.getLogger('sistema_limpeza')

class SistemaLimpeza:
    def __init__(self):
        """
        Inicializa o sistema de limpeza de arquivos temporários.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "limpeza.json")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de limpeza."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "limpeza.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de limpeza."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "limpeza_automatica": True,
                "intervalo_dias": 30,
                "ultima_limpeza": None,
                "diretorios_temporarios": [
                    "logs",
                    "temp",
                    "diagnostico"
                ],
                "padroes_arquivos_temporarios": [
                    "*.tmp",
                    "*.bak",
                    "*.log.*",
                    "backup_*_????????_??????.zip"
                ],
                "max_idade_logs_dias": 90,
                "max_idade_backups_dias": 180,
                "max_idade_diagnosticos_dias": 60,
                "max_idade_temporarios_dias": 7,
                "preservar_logs_recentes": 10,
                "preservar_backups_recentes": 5
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de limpeza criado")
    
    def identificar_arquivos_temporarios(self):
        """
        Identifica arquivos temporários que podem ser removidos.
        
        Returns:
            dict: Informações sobre arquivos temporários
        """
        logger.info("Identificando arquivos temporários...")
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            resultado = {
                "arquivos_temporarios": [],
                "logs_antigos": [],
                "backups_antigos": [],
                "diagnosticos_antigos": [],
                "total_tamanho_bytes": 0,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Data atual
            data_atual = datetime.datetime.now()
            
            # Verificar diretórios temporários
            for diretorio_rel in config["diretorios_temporarios"]:
                diretorio = os.path.join(self.diretorio_base, diretorio_rel)
                
                if not os.path.exists(diretorio) or not os.path.isdir(diretorio):
                    continue
                
                # Processar diretório de logs
                if diretorio_rel == "logs":
                    self._processar_logs(diretorio, resultado, config, data_atual)
                
                # Processar diretório de backups
                elif diretorio_rel.startswith("backups"):
                    self._processar_backups(diretorio, resultado, config, data_atual)
                
                # Processar diretório de diagnósticos
                elif diretorio_rel == "diagnostico":
                    self._processar_diagnosticos(diretorio, resultado, config, data_atual)
                
                # Processar outros diretórios temporários
                else:
                    self._processar_temporarios(diretorio, resultado, config, data_atual)
            
            # Calcular tamanho total
            resultado["total_tamanho_bytes"] = sum(arquivo["tamanho_bytes"] for arquivo in resultado["arquivos_temporarios"]) + \
                                              sum(arquivo["tamanho_bytes"] for arquivo in resultado["logs_antigos"]) + \
                                              sum(arquivo["tamanho_bytes"] for arquivo in resultado["backups_antigos"]) + \
                                              sum(arquivo["tamanho_bytes"] for arquivo in resultado["diagnosticos_antigos"])
            
            resultado["total_tamanho_mb"] = round(resultado["total_tamanho_bytes"] / (1024 * 1024), 2)
            
            logger.info(f"Identificados {len(resultado['arquivos_temporarios'])} arquivos temporários, " + 
                       f"{len(resultado['logs_antigos'])} logs antigos, " + 
                       f"{len(resultado['backups_antigos'])} backups antigos e " + 
                       f"{len(resultado['diagnosticos_antigos'])} diagnósticos antigos " + 
                       f"totalizando {resultado['total_tamanho_mb']} MB")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao identificar arquivos temporários: {str(e)}")
            return {
                "erro": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _processar_logs(self, diretorio, resultado, config, data_atual):
        """
        Processa o diretório de logs.
        
        Args:
            diretorio: Caminho do diretório
            resultado: Dicionário de resultado
            config: Configuração
            data_atual: Data atual
        """
        # Listar arquivos de log
        arquivos = []
        for arquivo in os.listdir(diretorio):
            caminho = os.path.join(diretorio, arquivo)
            
            if not os.path.isfile(caminho):
                continue
            
            # Verificar se é um arquivo de log
            if arquivo.endswith('.log') or re.match(r'.*\.log\.\d+', arquivo):
                data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
                idade_dias = (data_atual - data_modificacao).days
                
                arquivos.append({
                    "caminho": caminho,
                    "nome": arquivo,
                    "data_modificacao": data_modificacao,
                    "idade_dias": idade_dias,
                    "tamanho_bytes": os.path.getsize(caminho)
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        arquivos.sort(key=lambda x: x["data_modificacao"], reverse=True)
        
        # Preservar logs recentes
        logs_preservados = arquivos[:config["preservar_logs_recentes"]]
        logs_antigos = arquivos[config["preservar_logs_recentes"]:]
        
        # Filtrar por idade
        logs_antigos = [log for log in logs_antigos if log["idade_dias"] > config["max_idade_logs_dias"]]
        
        resultado["logs_antigos"].extend(logs_antigos)
    
    def _processar_backups(self, diretorio, resultado, config, data_atual):
        """
        Processa o diretório de backups.
        
        Args:
            diretorio: Caminho do diretório
            resultado: Dicionário de resultado
            config: Configuração
            data_atual: Data atual
        """
        # Listar arquivos de backup
        arquivos = []
        for arquivo in os.listdir(diretorio):
            caminho = os.path.join(diretorio, arquivo)
            
            if not os.path.isfile(caminho):
                continue
            
            # Verificar se é um arquivo de backup
            if arquivo.endswith('.zip') and arquivo.startswith('backup_'):
                data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
                idade_dias = (data_atual - data_modificacao).days
                
                arquivos.append({
                    "caminho": caminho,
                    "nome": arquivo,
                    "data_modificacao": data_modificacao,
                    "idade_dias": idade_dias,
                    "tamanho_bytes": os.path.getsize(caminho)
                })
        
        # Ordenar por data de modificação (mais recente primeiro)
        arquivos.sort(key=lambda x: x["data_modificacao"], reverse=True)
        
        # Preservar backups recentes
        backups_preservados = arquivos[:config["preservar_backups_recentes"]]
        backups_antigos = arquivos[config["preservar_backups_recentes"]:]
        
        # Filtrar por idade
        backups_antigos = [backup for backup in backups_antigos if backup["idade_dias"] > config["max_idade_backups_dias"]]
        
        resultado["backups_antigos"].extend(backups_antigos)
    
    def _processar_diagnosticos(self, diretorio, resultado, config, data_atual):
        """
        Processa o diretório de diagnósticos.
        
        Args:
            diretorio: Caminho do diretório
            resultado: Dicionário de resultado
            config: Configuração
            data_atual: Data atual
        """
        # Listar arquivos de diagnóstico
        for arquivo in os.listdir(diretorio):
            caminho = os.path.join(diretorio, arquivo)
            
            if not os.path.isfile(caminho):
                continue
            
            # Verificar se é um arquivo de diagnóstico
            if arquivo.startswith('relatorio_') or arquivo.startswith('verificacao_'):
                data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
                idade_dias = (data_atual - data_modificacao).days
                
                if idade_dias > config["max_idade_diagnosticos_dias"]:
                    resultado["diagnosticos_antigos"].append({
                        "caminho": caminho,
                        "nome": arquivo,
                        "data_modificacao": data_modificacao.isoformat(),
                        "idade_dias": idade_dias,
                        "tamanho_bytes": os.path.getsize(caminho)
                    })
    
    def _processar_temporarios(self, diretorio, resultado, config, data_atual):
        """
        Processa um diretório temporário genérico.
        
        Args:
            diretorio: Caminho do diretório
            resultado: Dicionário de resultado
            config: Configuração
            data_atual: Data atual
        """
        # Listar arquivos temporários
        for root, dirs, files in os.walk(diretorio):
            for arquivo in files:
                caminho = os.path.join(root, arquivo)
                
                # Verificar se corresponde a algum padrão de arquivo temporário
                for padrao in config["padroes_arquivos_temporarios"]:
                    if self._corresponde_padrao(arquivo, padrao):
                        data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(caminho))
                        idade_dias = (data_atual - data_modificacao).days
                        
                        if idade_dias > config["max_idade_temporarios_dias"]:
                            resultado["arquivos_temporarios"].append({
                                "caminho": caminho,
                                "nome": arquivo,
                                "data_modificacao": data_modificacao.isoformat(),
                                "idade_dias": idade_dias,
                                "tamanho_bytes": os.path.getsize(caminho)
                            })
                        
                        break
    
    def _corresponde_padrao(self, nome_arquivo, padrao):
        """
        Verifica se um nome de arquivo corresponde a um padrão.
        
        Args:
            nome_arquivo: Nome do arquivo
            padrao: Padrão (com wildcards)
            
        Returns:
            bool: True se corresponder, False caso contrário
        """
        # Converter padrão para regex
        regex = padrao.replace('.', '\\.').replace('*', '.*').replace('?', '.')
        return bool(re.match(f'^{regex}$', nome_arquivo))
    
    def limpar_arquivos_temporarios(self, categorias=None):
        """
        Remove arquivos temporários identificados.
        
        Args:
            categorias: Lista de categorias a limpar (None para todas)
            
        Returns:
            dict: Resultado da limpeza
        """
        logger.info("Limpando arquivos temporários...")
        
        try:
            # Identificar arquivos temporários
            arquivos = self.identificar_arquivos_temporarios()
            
            if "erro" in arquivos:
                return {
                    "sucesso": False,
                    "mensagem": f"Erro ao identificar arquivos temporários: {arquivos['erro']}"
                }
            
            # Definir categorias a limpar
            if categorias is None:
                categorias = ["arquivos_temporarios", "logs_antigos", "backups_antigos", "diagnosticos_antigos"]
            
            # Inicializar resultado
            resultado = {
                "sucesso": True,
                "arquivos_removidos": 0,
                "tamanho_liberado_bytes": 0,
                "erros": [],
                "detalhes": {}
            }
            
            # Processar cada categoria
            for categoria in categorias:
                if categoria not in arquivos:
                    continue
                
                resultado["detalhes"][categoria] = {
                    "total": len(arquivos[categoria]),
                    "removidos": 0,
                    "erros": 0
                }
                
                for arquivo in arquivos[categoria]:
                    try:
                        if os.path.exists(arquivo["caminho"]):
                            os.remove(arquivo["caminho"])
                            resultado["arquivos_removidos"] += 1
                            resultado["tamanho_liberado_bytes"] += arquivo["tamanho_bytes"]
                            resultado["detalhes"][categoria]["removidos"] += 1
                    except Exception as e:
                        resultado["erros"].append({
                            "arquivo": arquivo["caminho"],
                            "erro": str(e)
                        })
                        resultado["detalhes"][categoria]["erros"] += 1
            
            # Converter para MB
            resultado["tamanho_liberado_mb"] = round(resultado["tamanho_liberado_bytes"] / (1024 * 1024), 2)
            
            # Atualizar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config["ultima_limpeza"] = datetime.datetime.now().isoformat()
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Limpeza concluída: {resultado['arquivos_removidos']} arquivos removidos, " + 
                       f"{resultado['tamanho_liberado_mb']} MB liberados, {len(resultado['erros'])} erros")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": str(e),
                "traceback": traceback.format_exc()
            }
    
    def verificar_limpeza_automatica(self):
        """
        Verifica se é necessário realizar uma limpeza automática.
        
        Returns:
            bool: True se uma limpeza automática foi realizada, False caso contrário
        """
        try:
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar se a limpeza automática está ativada
            if not config.get("limpeza_automatica", True):
                return False
            
            # Verificar a data da última limpeza
            ultima_limpeza = config.get("ultima_limpeza")
            if not ultima_limpeza:
                # Nunca foi feita uma limpeza, fazer agora
                self.limpar_arquivos_temporarios()
                return True
            
            # Converter para datetime
            ultima_data = datetime.datetime.fromisoformat(ultima_limpeza)
            agora = datetime.datetime.now()
            
            # Calcular diferença em dias
            diferenca_dias = (agora - ultima_data).days
            
            # Verificar se passou o intervalo configurado
            if diferenca_dias >= config.get("intervalo_dias", 30):
                self.limpar_arquivos_temporarios()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar limpeza automática: {str(e)}")
            return False

# Função para integração com a aplicação principal
def verificar_limpeza_automatica_ao_iniciar(app):
    """
    Função para verificar e executar limpeza automática ao iniciar a aplicação.
    
    Args:
        app: Instância da aplicação Flask
    """
    @app.before_first_request
    def verificar_limpeza():
        try:
            sistema_limpeza = SistemaLimpeza()
            sistema_limpeza.verificar_limpeza_automatica()
        except Exception as e:
            # Registrar erro, mas não interromper a inicialização
            print(f"Erro ao verificar limpeza automática: {str(e)}")

# Adicionar rotas para o sistema de limpeza
def adicionar_rotas_limpeza(app):
    """
    Adiciona rotas para o sistema de limpeza à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify
    
    @app.route('/manutencao/limpeza')
    def pagina_limpeza():
        sistema_limpeza = SistemaLimpeza()
        
        # Carregar configuração
        with open(sistema_limpeza.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Identificar arquivos temporários
        arquivos = sistema_limpeza.identificar_arquivos_temporarios()
        
        return jsonify({
            "configuracoes": {
                "limpeza_automatica": config["limpeza_automatica"],
                "intervalo_dias": config["intervalo_dias"],
                "ultima_limpeza": config["ultima_limpeza"],
                "max_idade_logs_dias": config["max_idade_logs_dias"],
                "max_idade_backups_dias": config["max_idade_backups_dias"],
                "max_idade_diagnosticos_dias": config["max_idade_diagnosticos_dias"],
                "max_idade_temporarios_dias": config["max_idade_temporarios_dias"],
                "preservar_logs_recentes": config["preservar_logs_recentes"],
                "preservar_backups_recentes": config["preservar_backups_recentes"]
            },
            "arquivos_temporarios": {
                "total": len(arquivos.get("arquivos_temporarios", [])),
                "tamanho_mb": round(sum(a.get("tamanho_bytes", 0) for a in arquivos.get("arquivos_temporarios", [])) / (1024 * 1024), 2)
            },
            "logs_antigos": {
                "total": len(arquivos.get("logs_antigos", [])),
                "tamanho_mb": round(sum(a.get("tamanho_bytes", 0) for a in arquivos.get("logs_antigos", [])) / (1024 * 1024), 2)
            },
            "backups_antigos": {
                "total": len(arquivos.get("backups_antigos", [])),
                "tamanho_mb": round(sum(a.get("tamanho_bytes", 0) for a in arquivos.get("backups_antigos", [])) / (1024 * 1024), 2)
            },
            "diagnosticos_antigos": {
                "total": len(arquivos.get("diagnosticos_antigos", [])),
                "tamanho_mb": round(sum(a.get("tamanho_bytes", 0) for a in arquivos.get("diagnosticos_antigos", [])) / (1024 * 1024), 2)
            },
            "total_tamanho_mb": arquivos.get("total_tamanho_mb", 0)
        })
    
    @app.route('/manutencao/limpeza/identificar', methods=['POST'])
    def identificar_temporarios():
        sistema_limpeza = SistemaLimpeza()
        
        arquivos = sistema_limpeza.identificar_arquivos_temporarios()
        
        return jsonify(arquivos)
    
    @app.route('/manutencao/limpeza/limpar', methods=['POST'])
    def limpar_temporarios():
        sistema_limpeza = SistemaLimpeza()
        
        categorias = request.json.get('categorias')
        
        resultado = sistema_limpeza.limpar_arquivos_temporarios(categorias)
        
        return jsonify(resultado)
    
    @app.route('/manutencao/limpeza/configuracoes', methods=['POST'])
    def atualizar_configuracoes_limpeza():
        try:
            sistema_limpeza = SistemaLimpeza()
            
            # Carregar configuração atual
            with open(sistema_limpeza.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "limpeza_automatica" in dados:
                config["limpeza_automatica"] = dados["limpeza_automatica"]
            
            if "intervalo_dias" in dados:
                config["intervalo_dias"] = dados["intervalo_dias"]
            
            if "max_idade_logs_dias" in dados:
                config["max_idade_logs_dias"] = dados["max_idade_logs_dias"]
            
            if "max_idade_backups_dias" in dados:
                config["max_idade_backups_dias"] = dados["max_idade_backups_dias"]
            
            if "max_idade_diagnosticos_dias" in dados:
                config["max_idade_diagnosticos_dias"] = dados["max_idade_diagnosticos_dias"]
            
            if "max_idade_temporarios_dias" in dados:
                config["max_idade_temporarios_dias"] = dados["max_idade_temporarios_dias"]
            
            if "preservar_logs_recentes" in dados:
                config["preservar_logs_recentes"] = dados["preservar_logs_recentes"]
            
            if "preservar_backups_recentes" in dados:
                config["preservar_backups_recentes"] = dados["preservar_backups_recentes"]
            
            # Salvar configuração
            with open(sistema_limpeza.arquivo_config, 'w', encoding='utf-8') as f:
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
