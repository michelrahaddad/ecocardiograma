"""
Módulo de Diagnóstico e Relatórios de Desempenho

Este módulo implementa um sistema de diagnóstico e monitoramento de desempenho para o software de ecocardiograma.
Permite analisar o desempenho do sistema, identificar problemas e gerar relatórios.
"""

import os
import json
import sqlite3
import logging
import platform
import psutil
import time
import datetime
import threading
import traceback
import matplotlib.pyplot as plt
import io
import base64

# Configuração do logger
logger = logging.getLogger('sistema_diagnostico')

class SistemaDiagnostico:
    def __init__(self):
        """
        Inicializa o sistema de diagnóstico e monitoramento.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_diagnostico = os.path.join(self.diretorio_base, "diagnostico")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "diagnostico.json")
        self.arquivo_db = os.path.join(self.diretorio_base, "ecocardiograma.db")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_diagnostico, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
        
        # Inicializar monitoramento
        self.monitoramento_ativo = False
        self.thread_monitoramento = None
        self.dados_monitoramento = {
            "cpu": [],
            "memoria": [],
            "disco": [],
            "timestamp": []
        }
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de diagnóstico."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "diagnostico.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de diagnóstico."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "intervalo_monitoramento": 60,  # segundos
                "limite_cpu": 80,  # porcentagem
                "limite_memoria": 80,  # porcentagem
                "limite_disco": 90,  # porcentagem
                "monitoramento_automatico": False,
                "notificar_limites": True,
                "max_registros_monitoramento": 1000
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de diagnóstico criado")
    
    def obter_info_sistema(self):
        """
        Obtém informações do sistema.
        
        Returns:
            dict: Informações do sistema
        """
        try:
            # Informações do sistema operacional
            info_sistema = {
                "sistema_operacional": platform.system(),
                "versao_so": platform.version(),
                "arquitetura": platform.machine(),
                "processador": platform.processor(),
                "python_versao": platform.python_version(),
                "hostname": platform.node()
            }
            
            # Informações de hardware
            info_hardware = {
                "cpu_nucleos_fisicos": psutil.cpu_count(logical=False),
                "cpu_nucleos_logicos": psutil.cpu_count(logical=True),
                "cpu_uso": psutil.cpu_percent(interval=1),
                "memoria_total": round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2),  # GB
                "memoria_disponivel": round(psutil.virtual_memory().available / (1024 * 1024 * 1024), 2),  # GB
                "memoria_uso_percentual": psutil.virtual_memory().percent
            }
            
            # Informações de disco
            discos = []
            for particao in psutil.disk_partitions():
                try:
                    uso = psutil.disk_usage(particao.mountpoint)
                    discos.append({
                        "dispositivo": particao.device,
                        "ponto_montagem": particao.mountpoint,
                        "sistema_arquivos": particao.fstype,
                        "total_gb": round(uso.total / (1024 * 1024 * 1024), 2),
                        "usado_gb": round(uso.used / (1024 * 1024 * 1024), 2),
                        "livre_gb": round(uso.free / (1024 * 1024 * 1024), 2),
                        "percentual_uso": uso.percent
                    })
                except:
                    # Algumas partições podem não ser acessíveis
                    pass
            
            # Informações de rede
            interfaces_rede = []
            for nome, stats in psutil.net_if_stats().items():
                interfaces_rede.append({
                    "nome": nome,
                    "status": "Ativo" if stats.isup else "Inativo",
                    "velocidade": stats.speed
                })
            
            # Informações do banco de dados
            info_banco_dados = self.diagnosticar_banco_dados()
            
            return {
                "sistema": info_sistema,
                "hardware": info_hardware,
                "discos": discos,
                "rede": interfaces_rede,
                "banco_dados": info_banco_dados,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {str(e)}")
            return {"erro": str(e)}
    
    def diagnosticar_banco_dados(self):
        """
        Realiza diagnóstico do banco de dados.
        
        Returns:
            dict: Informações do banco de dados
        """
        try:
            if not os.path.exists(self.arquivo_db):
                return {
                    "status": "Não encontrado",
                    "mensagem": "Banco de dados não encontrado"
                }
            
            # Tamanho do arquivo
            tamanho_bytes = os.path.getsize(self.arquivo_db)
            tamanho_mb = round(tamanho_bytes / (1024 * 1024), 2)
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar integridade
            cursor.execute("PRAGMA integrity_check")
            integridade = cursor.fetchone()[0]
            
            # Obter estatísticas das tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            
            estatisticas_tabelas = []
            for tabela in tabelas:
                nome_tabela = tabela[0]
                
                # Ignorar tabelas do sistema
                if nome_tabela.startswith('sqlite_'):
                    continue
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
                count = cursor.fetchone()[0]
                
                estatisticas_tabelas.append({
                    "nome": nome_tabela,
                    "registros": count
                })
            
            conn.close()
            
            return {
                "status": "OK" if integridade == "ok" else "Erro",
                "tamanho_mb": tamanho_mb,
                "integridade": integridade,
                "tabelas": estatisticas_tabelas
            }
            
        except Exception as e:
            logger.error(f"Erro ao diagnosticar banco de dados: {str(e)}")
            return {
                "status": "Erro",
                "mensagem": str(e)
            }
    
    def verificar_integridade_arquivos(self):
        """
        Verifica a integridade dos arquivos do sistema.
        
        Returns:
            dict: Resultado da verificação
        """
        try:
            resultado = {
                "status": "OK",
                "arquivos_verificados": 0,
                "arquivos_faltando": [],
                "arquivos_corrompidos": [],
                "detalhes": []
            }
            
            # Lista de arquivos essenciais
            arquivos_essenciais = [
                os.path.join(self.diretorio_base, "ecocardiograma.db"),
                os.path.join(self.diretorio_base, "src", "main.py"),
                os.path.join(self.diretorio_base, "src", "integracao_modelos.py")
            ]
            
            # Verificar existência dos arquivos essenciais
            for arquivo in arquivos_essenciais:
                if not os.path.exists(arquivo):
                    resultado["arquivos_faltando"].append(arquivo)
                    resultado["status"] = "Erro"
                else:
                    resultado["arquivos_verificados"] += 1
                    
                    # Verificar se é um arquivo Python
                    if arquivo.endswith('.py'):
                        try:
                            with open(arquivo, 'r', encoding='utf-8') as f:
                                conteudo = f.read()
                            
                            # Tentar compilar para verificar sintaxe
                            compile(conteudo, arquivo, 'exec')
                        except Exception as e:
                            resultado["arquivos_corrompidos"].append({
                                "arquivo": arquivo,
                                "erro": str(e)
                            })
                            resultado["status"] = "Erro"
            
            # Verificar diretórios importantes
            diretorios_importantes = [
                os.path.join(self.diretorio_base, "src", "modelos_laudo"),
                os.path.join(self.diretorio_base, "src", "static"),
                os.path.join(self.diretorio_base, "src", "templates")
            ]
            
            for diretorio in diretorios_importantes:
                if not os.path.exists(diretorio) or not os.path.isdir(diretorio):
                    resultado["detalhes"].append({
                        "tipo": "diretorio_faltando",
                        "caminho": diretorio
                    })
                    resultado["status"] = "Erro"
                else:
                    # Verificar se o diretório não está vazio
                    if len(os.listdir(diretorio)) == 0:
                        resultado["detalhes"].append({
                            "tipo": "diretorio_vazio",
                            "caminho": diretorio
                        })
                        resultado["status"] = "Aviso"
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar integridade dos arquivos: {str(e)}")
            return {
                "status": "Erro",
                "mensagem": str(e)
            }
    
    def iniciar_monitoramento(self):
        """
        Inicia o monitoramento contínuo do sistema.
        
        Returns:
            bool: True se o monitoramento foi iniciado, False caso contrário
        """
        if self.monitoramento_ativo:
            logger.warning("Monitoramento já está ativo")
            return False
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            intervalo = config.get("intervalo_monitoramento", 60)
            
            # Limpar dados anteriores
            self.dados_monitoramento = {
                "cpu": [],
                "memoria": [],
                "disco": [],
                "timestamp": []
            }
            
            # Iniciar thread de monitoramento
            self.monitoramento_ativo = True
            self.thread_monitoramento = threading.Thread(target=self._thread_monitoramento, args=(intervalo,))
            self.thread_monitoramento.daemon = True
            self.thread_monitoramento.start()
            
            logger.info(f"Monitoramento iniciado com intervalo de {intervalo} segundos")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento: {str(e)}")
            return False
    
    def parar_monitoramento(self):
        """
        Para o monitoramento contínuo do sistema.
        
        Returns:
            bool: True se o monitoramento foi parado, False caso contrário
        """
        if not self.monitoramento_ativo:
            logger.warning("Monitoramento não está ativo")
            return False
        
        try:
            self.monitoramento_ativo = False
            
            # Aguardar thread terminar
            if self.thread_monitoramento and self.thread_monitoramento.is_alive():
                self.thread_monitoramento.join(timeout=5)
            
            logger.info("Monitoramento parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar monitoramento: {str(e)}")
            return False
    
    def _thread_monitoramento(self, intervalo):
        """
        Thread de monitoramento contínuo.
        
        Args:
            intervalo: Intervalo em segundos entre as medições
        """
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            max_registros = config.get("max_registros_monitoramento", 1000)
            limite_cpu = config.get("limite_cpu", 80)
            limite_memoria = config.get("limite_memoria", 80)
            limite_disco = config.get("limite_disco", 90)
            notificar_limites = config.get("notificar_limites", True)
            
            while self.monitoramento_ativo:
                try:
                    # Coletar dados
                    cpu_uso = psutil.cpu_percent(interval=1)
                    memoria_uso = psutil.virtual_memory().percent
                    
                    # Uso do disco onde está o banco de dados
                    disco_uso = 0
                    if os.path.exists(self.arquivo_db):
                        diretorio_db = os.path.dirname(self.arquivo_db)
                        disco_uso = psutil.disk_usage(diretorio_db).percent
                    
                    timestamp = datetime.datetime.now().isoformat()
                    
                    # Adicionar aos dados de monitoramento
                    self.dados_monitoramento["cpu"].append(cpu_uso)
                    self.dados_monitoramento["memoria"].append(memoria_uso)
                    self.dados_monitoramento["disco"].append(disco_uso)
                    self.dados_monitoramento["timestamp"].append(timestamp)
                    
                    # Limitar número de registros
                    if len(self.dados_monitoramento["cpu"]) > max_registros:
                        self.dados_monitoramento["cpu"].pop(0)
                        self.dados_monitoramento["memoria"].pop(0)
                        self.dados_monitoramento["disco"].pop(0)
                        self.dados_monitoramento["timestamp"].pop(0)
                    
                    # Verificar limites
                    if notificar_limites:
                        if cpu_uso > limite_cpu:
                            logger.warning(f"Uso de CPU acima do limite: {cpu_uso}% (limite: {limite_cpu}%)")
                        
                        if memoria_uso > limite_memoria:
                            logger.warning(f"Uso de memória acima do limite: {memoria_uso}% (limite: {limite_memoria}%)")
                        
                        if disco_uso > limite_disco:
                            logger.warning(f"Uso de disco acima do limite: {disco_uso}% (limite: {limite_disco}%)")
                    
                    # Aguardar próxima medição
                    time.sleep(intervalo)
                    
                except Exception as e:
                    logger.error(f"Erro na thread de monitoramento: {str(e)}")
                    time.sleep(intervalo)
            
        except Exception as e:
            logger.error(f"Erro fatal na thread de monitoramento: {str(e)}")
    
    def gerar_relatorio_desempenho(self):
        """
        Gera um relatório de desempenho do sistema.
        
        Returns:
            dict: Relatório de desempenho
        """
        try:
            # Obter informações do sistema
            info_sistema = self.obter_info_sistema()
            
            # Verificar integridade dos arquivos
            integridade_arquivos = self.verificar_integridade_arquivos()
            
            # Dados de monitoramento
            dados_monitoramento = None
            if self.dados_monitoramento["cpu"]:
                dados_monitoramento = {
                    "cpu": {
                        "media": sum(self.dados_monitoramento["cpu"]) / len(self.dados_monitoramento["cpu"]),
                        "max": max(self.dados_monitoramento["cpu"]),
                        "min": min(self.dados_monitoramento["cpu"]),
                        "atual": self.dados_monitoramento["cpu"][-1]
                    },
                    "memoria": {
                        "media": sum(self.dados_monitoramento["memoria"]) / len(self.dados_monitoramento["memoria"]),
                        "max": max(self.dados_monitoramento["memoria"]),
                        "min": min(self.dados_monitoramento["memoria"]),
                        "atual": self.dados_monitoramento["memoria"][-1]
                    },
                    "disco": {
                        "media": sum(self.dados_monitoramento["disco"]) / len(self.dados_monitoramento["disco"]),
                        "max": max(self.dados_monitoramento["disco"]),
                        "min": min(self.dados_monitoramento["disco"]),
                        "atual": self.dados_monitoramento["disco"][-1]
                    },
                    "periodo": {
                        "inicio": self.dados_monitoramento["timestamp"][0],
                        "fim": self.dados_monitoramento["timestamp"][-1],
                        "amostras": len(self.dados_monitoramento["timestamp"])
                    }
                }
            
            # Gerar gráficos
            graficos = None
            if self.dados_monitoramento["cpu"]:
                graficos = self._gerar_graficos_monitoramento()
            
            # Montar relatório
            relatorio = {
                "sistema": info_sistema,
                "integridade_arquivos": integridade_arquivos,
                "monitoramento": dados_monitoramento,
                "graficos": graficos,
                "timestamp": datetime.datetime.now().isoformat(),
                "status_geral": "OK"
            }
            
            # Determinar status geral
            if integridade_arquivos["status"] != "OK":
                relatorio["status_geral"] = integridade_arquivos["status"]
            
            if dados_monitoramento:
                # Carregar configuração
                with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                limite_cpu = config.get("limite_cpu", 80)
                limite_memoria = config.get("limite_memoria", 80)
                limite_disco = config.get("limite_disco", 90)
                
                if dados_monitoramento["cpu"]["atual"] > limite_cpu:
                    relatorio["status_geral"] = "Aviso"
                
                if dados_monitoramento["memoria"]["atual"] > limite_memoria:
                    relatorio["status_geral"] = "Aviso"
                
                if dados_monitoramento["disco"]["atual"] > limite_disco:
                    relatorio["status_geral"] = "Aviso"
            
            # Salvar relatório
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_desempenho_{timestamp}.json"
            caminho_arquivo = os.path.join(self.diretorio_diagnostico, nome_arquivo)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=4)
            
            logger.info(f"Relatório de desempenho gerado: {caminho_arquivo}")
            
            return relatorio
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de desempenho: {str(e)}")
            return {
                "erro": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _gerar_graficos_monitoramento(self):
        """
        Gera gráficos a partir dos dados de monitoramento.
        
        Returns:
            dict: Gráficos em formato base64
        """
        try:
            graficos = {}
            
            # Converter timestamps para formato legível
            timestamps = []
            for ts in self.dados_monitoramento["timestamp"]:
                dt = datetime.datetime.fromisoformat(ts)
                timestamps.append(dt.strftime("%H:%M:%S"))
            
            # Limitar número de pontos para melhor visualização
            max_pontos = 20
            if len(timestamps) > max_pontos:
                passo = len(timestamps) // max_pontos
                timestamps = timestamps[::passo]
                cpu_dados = self.dados_monitoramento["cpu"][::passo]
                memoria_dados = self.dados_monitoramento["memoria"][::passo]
                disco_dados = self.dados_monitoramento["disco"][::passo]
            else:
                cpu_dados = self.dados_monitoramento["cpu"]
                memoria_dados = self.dados_monitoramento["memoria"]
                disco_dados = self.dados_monitoramento["disco"]
            
            # Gráfico de CPU
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, cpu_dados, 'b-', label='CPU (%)')
            plt.title('Uso de CPU')
            plt.xlabel('Tempo')
            plt.ylabel('Uso (%)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Converter para base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graficos["cpu"] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            # Gráfico de Memória
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, memoria_dados, 'r-', label='Memória (%)')
            plt.title('Uso de Memória')
            plt.xlabel('Tempo')
            plt.ylabel('Uso (%)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Converter para base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graficos["memoria"] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            # Gráfico de Disco
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, disco_dados, 'g-', label='Disco (%)')
            plt.title('Uso de Disco')
            plt.xlabel('Tempo')
            plt.ylabel('Uso (%)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Converter para base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graficos["disco"] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            # Gráfico combinado
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, cpu_dados, 'b-', label='CPU (%)')
            plt.plot(timestamps, memoria_dados, 'r-', label='Memória (%)')
            plt.plot(timestamps, disco_dados, 'g-', label='Disco (%)')
            plt.title('Uso de Recursos do Sistema')
            plt.xlabel('Tempo')
            plt.ylabel('Uso (%)')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Converter para base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            graficos["combinado"] = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return graficos
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráficos de monitoramento: {str(e)}")
            return None

# Função para integração com a aplicação principal
def configurar_diagnostico_aplicacao(app):
    """
    Configura o sistema de diagnóstico para a aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    sistema_diagnostico = SistemaDiagnostico()
    
    # Carregar configuração
    with open(sistema_diagnostico.arquivo_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Iniciar monitoramento automático se configurado
    if config.get("monitoramento_automatico", False):
        @app.before_first_request
        def iniciar_monitoramento_automatico():
            sistema_diagnostico.iniciar_monitoramento()

# Adicionar rotas para o sistema de diagnóstico
def adicionar_rotas_diagnostico(app):
    """
    Adiciona rotas para o sistema de diagnóstico à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify, send_file, render_template_string
    
    @app.route('/manutencao/diagnostico')
    def pagina_diagnostico():
        sistema_diagnostico = SistemaDiagnostico()
        
        # Carregar configuração
        with open(sistema_diagnostico.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Obter informações do sistema
        info_sistema = sistema_diagnostico.obter_info_sistema()
        
        return jsonify({
            "configuracoes": {
                "intervalo_monitoramento": config["intervalo_monitoramento"],
                "limite_cpu": config["limite_cpu"],
                "limite_memoria": config["limite_memoria"],
                "limite_disco": config["limite_disco"],
                "monitoramento_automatico": config["monitoramento_automatico"],
                "notificar_limites": config["notificar_limites"],
                "max_registros_monitoramento": config["max_registros_monitoramento"]
            },
            "sistema": info_sistema,
            "monitoramento_ativo": sistema_diagnostico.monitoramento_ativo
        })
    
    @app.route('/manutencao/diagnostico/iniciar_monitoramento', methods=['POST'])
    def iniciar_monitoramento():
        sistema_diagnostico = SistemaDiagnostico()
        
        resultado = sistema_diagnostico.iniciar_monitoramento()
        
        return jsonify({
            "sucesso": resultado,
            "mensagem": "Monitoramento iniciado com sucesso" if resultado else "Falha ao iniciar monitoramento"
        })
    
    @app.route('/manutencao/diagnostico/parar_monitoramento', methods=['POST'])
    def parar_monitoramento():
        sistema_diagnostico = SistemaDiagnostico()
        
        resultado = sistema_diagnostico.parar_monitoramento()
        
        return jsonify({
            "sucesso": resultado,
            "mensagem": "Monitoramento parado com sucesso" if resultado else "Falha ao parar monitoramento"
        })
    
    @app.route('/manutencao/diagnostico/relatorio')
    def gerar_relatorio():
        sistema_diagnostico = SistemaDiagnostico()
        
        relatorio = sistema_diagnostico.gerar_relatorio_desempenho()
        
        return jsonify(relatorio)
    
    @app.route('/manutencao/diagnostico/relatorio_html')
    def relatorio_html():
        sistema_diagnostico = SistemaDiagnostico()
        
        relatorio = sistema_diagnostico.gerar_relatorio_desempenho()
        
        # Template HTML para o relatório
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório de Desempenho</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                .status-ok { color: green; }
                .status-aviso { color: orange; }
                .status-erro { color: red; }
                table { border-collapse: collapse; width: 100%; margin-top: 10px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .grafico { margin-top: 20px; text-align: center; }
                .grafico img { max-width: 100%; height: auto; }
            </style>
        </head>
        <body>
            <h1>Relatório de Desempenho do Sistema</h1>
            <p>Gerado em: {{ relatorio.timestamp }}</p>
            
            <h2>Status Geral: 
                <span class="status-{{ 'ok' if relatorio.status_geral == 'OK' else 'aviso' if relatorio.status_geral == 'Aviso' else 'erro' }}">
                    {{ relatorio.status_geral }}
                </span>
            </h2>
            
            <h2>Informações do Sistema</h2>
            <table>
                <tr>
                    <th>Sistema Operacional</th>
                    <td>{{ relatorio.sistema.sistema.sistema_operacional }} {{ relatorio.sistema.sistema.versao_so }}</td>
                </tr>
                <tr>
                    <th>Arquitetura</th>
                    <td>{{ relatorio.sistema.sistema.arquitetura }}</td>
                </tr>
                <tr>
                    <th>Processador</th>
                    <td>{{ relatorio.sistema.sistema.processador }}</td>
                </tr>
                <tr>
                    <th>Versão Python</th>
                    <td>{{ relatorio.sistema.sistema.python_versao }}</td>
                </tr>
                <tr>
                    <th>Hostname</th>
                    <td>{{ relatorio.sistema.sistema.hostname }}</td>
                </tr>
            </table>
            
            <h2>Hardware</h2>
            <table>
                <tr>
                    <th>CPU (Núcleos Físicos/Lógicos)</th>
                    <td>{{ relatorio.sistema.hardware.cpu_nucleos_fisicos }} / {{ relatorio.sistema.hardware.cpu_nucleos_logicos }}</td>
                </tr>
                <tr>
                    <th>Uso de CPU</th>
                    <td>{{ relatorio.sistema.hardware.cpu_uso }}%</td>
                </tr>
                <tr>
                    <th>Memória Total</th>
                    <td>{{ relatorio.sistema.hardware.memoria_total }} GB</td>
                </tr>
                <tr>
                    <th>Memória Disponível</th>
                    <td>{{ relatorio.sistema.hardware.memoria_disponivel }} GB</td>
                </tr>
                <tr>
                    <th>Uso de Memória</th>
                    <td>{{ relatorio.sistema.hardware.memoria_uso_percentual }}%</td>
                </tr>
            </table>
            
            <h2>Discos</h2>
            <table>
                <tr>
                    <th>Dispositivo</th>
                    <th>Ponto de Montagem</th>
                    <th>Sistema de Arquivos</th>
                    <th>Total (GB)</th>
                    <th>Usado (GB)</th>
                    <th>Livre (GB)</th>
                    <th>Uso (%)</th>
                </tr>
                {% for disco in relatorio.sistema.discos %}
                <tr>
                    <td>{{ disco.dispositivo }}</td>
                    <td>{{ disco.ponto_montagem }}</td>
                    <td>{{ disco.sistema_arquivos }}</td>
                    <td>{{ disco.total_gb }}</td>
                    <td>{{ disco.usado_gb }}</td>
                    <td>{{ disco.livre_gb }}</td>
                    <td>{{ disco.percentual_uso }}%</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>Banco de Dados</h2>
            <table>
                <tr>
                    <th>Status</th>
                    <td class="status-{{ 'ok' if relatorio.sistema.banco_dados.status == 'OK' else 'erro' }}">
                        {{ relatorio.sistema.banco_dados.status }}
                    </td>
                </tr>
                <tr>
                    <th>Tamanho</th>
                    <td>{{ relatorio.sistema.banco_dados.tamanho_mb }} MB</td>
                </tr>
                <tr>
                    <th>Integridade</th>
                    <td>{{ relatorio.sistema.banco_dados.integridade }}</td>
                </tr>
            </table>
            
            <h3>Tabelas</h3>
            <table>
                <tr>
                    <th>Nome</th>
                    <th>Registros</th>
                </tr>
                {% for tabela in relatorio.sistema.banco_dados.tabelas %}
                <tr>
                    <td>{{ tabela.nome }}</td>
                    <td>{{ tabela.registros }}</td>
                </tr>
                {% endfor %}
            </table>
            
            <h2>Verificação de Integridade de Arquivos</h2>
            <p>Status: 
                <span class="status-{{ 'ok' if relatorio.integridade_arquivos.status == 'OK' else 'aviso' if relatorio.integridade_arquivos.status == 'Aviso' else 'erro' }}">
                    {{ relatorio.integridade_arquivos.status }}
                </span>
            </p>
            <p>Arquivos verificados: {{ relatorio.integridade_arquivos.arquivos_verificados }}</p>
            
            {% if relatorio.integridade_arquivos.arquivos_faltando %}
            <h3>Arquivos Faltando</h3>
            <ul>
                {% for arquivo in relatorio.integridade_arquivos.arquivos_faltando %}
                <li>{{ arquivo }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            {% if relatorio.integridade_arquivos.arquivos_corrompidos %}
            <h3>Arquivos Corrompidos</h3>
            <ul>
                {% for arquivo in relatorio.integridade_arquivos.arquivos_corrompidos %}
                <li>{{ arquivo.arquivo }}: {{ arquivo.erro }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            {% if relatorio.monitoramento %}
            <h2>Monitoramento de Desempenho</h2>
            <p>Período: {{ relatorio.monitoramento.periodo.inicio }} a {{ relatorio.monitoramento.periodo.fim }}</p>
            <p>Amostras: {{ relatorio.monitoramento.periodo.amostras }}</p>
            
            <h3>CPU</h3>
            <table>
                <tr>
                    <th>Média</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.cpu.media) }}%</td>
                </tr>
                <tr>
                    <th>Máximo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.cpu.max) }}%</td>
                </tr>
                <tr>
                    <th>Mínimo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.cpu.min) }}%</td>
                </tr>
                <tr>
                    <th>Atual</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.cpu.atual) }}%</td>
                </tr>
            </table>
            
            <h3>Memória</h3>
            <table>
                <tr>
                    <th>Média</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.memoria.media) }}%</td>
                </tr>
                <tr>
                    <th>Máximo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.memoria.max) }}%</td>
                </tr>
                <tr>
                    <th>Mínimo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.memoria.min) }}%</td>
                </tr>
                <tr>
                    <th>Atual</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.memoria.atual) }}%</td>
                </tr>
            </table>
            
            <h3>Disco</h3>
            <table>
                <tr>
                    <th>Média</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.disco.media) }}%</td>
                </tr>
                <tr>
                    <th>Máximo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.disco.max) }}%</td>
                </tr>
                <tr>
                    <th>Mínimo</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.disco.min) }}%</td>
                </tr>
                <tr>
                    <th>Atual</th>
                    <td>{{ "%.2f"|format(relatorio.monitoramento.disco.atual) }}%</td>
                </tr>
            </table>
            
            {% if relatorio.graficos %}
            <h2>Gráficos de Desempenho</h2>
            
            <div class="grafico">
                <h3>Uso Combinado de Recursos</h3>
                <img src="data:image/png;base64,{{ relatorio.graficos.combinado }}" alt="Gráfico de Uso Combinado">
            </div>
            
            <div class="grafico">
                <h3>Uso de CPU</h3>
                <img src="data:image/png;base64,{{ relatorio.graficos.cpu }}" alt="Gráfico de CPU">
            </div>
            
            <div class="grafico">
                <h3>Uso de Memória</h3>
                <img src="data:image/png;base64,{{ relatorio.graficos.memoria }}" alt="Gráfico de Memória">
            </div>
            
            <div class="grafico">
                <h3>Uso de Disco</h3>
                <img src="data:image/png;base64,{{ relatorio.graficos.disco }}" alt="Gráfico de Disco">
            </div>
            {% endif %}
            {% endif %}
            
            <hr>
            <p><em>Relatório gerado automaticamente pelo Sistema de Diagnóstico.</em></p>
        </body>
        </html>
        """
        
        # Renderizar template
        html = render_template_string(html_template, relatorio=relatorio)
        
        # Salvar HTML
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_desempenho_{timestamp}.html"
        caminho_arquivo = os.path.join(sistema_diagnostico.diretorio_diagnostico, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return html
    
    @app.route('/manutencao/diagnostico/configuracoes', methods=['POST'])
    def atualizar_configuracoes_diagnostico():
        try:
            sistema_diagnostico = SistemaDiagnostico()
            
            # Carregar configuração atual
            with open(sistema_diagnostico.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            if "intervalo_monitoramento" in dados:
                config["intervalo_monitoramento"] = dados["intervalo_monitoramento"]
            
            if "limite_cpu" in dados:
                config["limite_cpu"] = dados["limite_cpu"]
            
            if "limite_memoria" in dados:
                config["limite_memoria"] = dados["limite_memoria"]
            
            if "limite_disco" in dados:
                config["limite_disco"] = dados["limite_disco"]
            
            if "monitoramento_automatico" in dados:
                config["monitoramento_automatico"] = dados["monitoramento_automatico"]
            
            if "notificar_limites" in dados:
                config["notificar_limites"] = dados["notificar_limites"]
            
            if "max_registros_monitoramento" in dados:
                config["max_registros_monitoramento"] = dados["max_registros_monitoramento"]
            
            # Salvar configuração
            with open(sistema_diagnostico.arquivo_config, 'w', encoding='utf-8') as f:
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
