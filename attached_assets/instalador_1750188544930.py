"""
Módulo de Instalador/Desinstalador

Este módulo implementa um sistema de instalação e desinstalação para o software de ecocardiograma.
Permite criar pacotes de instalação e desinstalar o software de forma limpa.
"""

import os
import sys
import json
import shutil
import logging
import platform
import subprocess
import tempfile
import zipfile
import datetime
import traceback

# Configuração do logger
logger = logging.getLogger('sistema_instalador')

class SistemaInstalador:
    def __init__(self):
        """
        Inicializa o sistema de instalação e desinstalação.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio_instalador = os.path.join(self.diretorio_base, "instalador")
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "instalador.json")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        os.makedirs(self.diretorio_instalador, exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de instalador."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "instalador.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração do instalador."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "versao": "1.0.0",
                "nome_aplicacao": "Ecocardiograma",
                "empresa": "Vidah",
                "autor": "Michel Raineri Haddad",
                "website": "https://vidah.com.br",
                "diretorio_instalacao_padrao": {
                    "windows": "C:\\Program Files\\Ecocardiograma",
                    "linux": "/opt/ecocardiograma",
                    "darwin": "/Applications/Ecocardiograma.app"
                },
                "arquivos_essenciais": [
                    "src/main.py",
                    "src/integracao_modelos.py",
                    "src/modelos_laudo/**",
                    "src/static/**",
                    "src/templates/**",
                    "requirements.txt"
                ],
                "criar_atalhos": True,
                "criar_menu_iniciar": True,
                "criar_desinstalador": True,
                "requisitos_sistema": {
                    "python_minimo": "3.8.0",
                    "espaco_disco_mb": 100,
                    "memoria_mb": 512
                }
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração do instalador criado")
    
    def criar_pacote_instalacao(self, destino=None):
        """
        Cria um pacote de instalação.
        
        Args:
            destino: Caminho para salvar o pacote (opcional)
            
        Returns:
            dict: Resultado da operação
        """
        logger.info("Criando pacote de instalação...")
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Determinar destino
            if not destino:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"instalador_{config['nome_aplicacao']}_{config['versao']}_{timestamp}.zip"
                destino = os.path.join(self.diretorio_instalador, nome_arquivo)
            
            # Criar diretório temporário
            diretorio_temp = tempfile.mkdtemp()
            
            # Copiar arquivos essenciais
            self._copiar_arquivos_essenciais(diretorio_temp, config["arquivos_essenciais"])
            
            # Criar scripts de instalação
            self._criar_scripts_instalacao(diretorio_temp, config)
            
            # Criar arquivo de metadados
            metadados = {
                "nome": config["nome_aplicacao"],
                "versao": config["versao"],
                "empresa": config["empresa"],
                "autor": config["autor"],
                "website": config["website"],
                "data_criacao": datetime.datetime.now().isoformat(),
                "sistema_operacional": platform.system(),
                "python_versao": platform.python_version()
            }
            
            with open(os.path.join(diretorio_temp, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=4)
            
            # Criar arquivo ZIP
            with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(diretorio_temp):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, diretorio_temp)
                        zipf.write(file_path, arcname)
            
            # Limpar diretório temporário
            shutil.rmtree(diretorio_temp)
            
            logger.info(f"Pacote de instalação criado: {destino}")
            return {
                "sucesso": True,
                "mensagem": "Pacote de instalação criado com sucesso",
                "caminho": destino
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar pacote de instalação: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao criar pacote de instalação: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def _copiar_arquivos_essenciais(self, destino, padroes):
        """
        Copia os arquivos essenciais para o diretório temporário.
        
        Args:
            destino: Diretório de destino
            padroes: Lista de padrões de arquivos
        """
        import glob
        
        # Criar diretório de arquivos
        diretorio_arquivos = os.path.join(destino, "files")
        os.makedirs(diretorio_arquivos, exist_ok=True)
        
        # Copiar arquivos
        for padrao in padroes:
            # Converter para caminho absoluto
            padrao_abs = os.path.join(self.diretorio_base, padrao)
            
            # Expandir padrão
            for arquivo in glob.glob(padrao_abs, recursive=True):
                if os.path.isfile(arquivo):
                    # Determinar caminho relativo
                    caminho_rel = os.path.relpath(arquivo, self.diretorio_base)
                    
                    # Criar diretório de destino
                    diretorio_destino = os.path.dirname(os.path.join(diretorio_arquivos, caminho_rel))
                    os.makedirs(diretorio_destino, exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(arquivo, os.path.join(diretorio_arquivos, caminho_rel))
    
    def _criar_scripts_instalacao(self, destino, config):
        """
        Cria os scripts de instalação.
        
        Args:
            destino: Diretório de destino
            config: Configuração do instalador
        """
        # Criar script de instalação para Windows
        script_windows = os.path.join(destino, "install.bat")
        with open(script_windows, 'w', newline='\r\n') as f:
            f.write("@echo off\n")
            f.write("echo Instalador do " + config["nome_aplicacao"] + " " + config["versao"] + "\n")
            f.write("echo.\n")
            f.write("echo Este instalador configurara o software " + config["nome_aplicacao"] + " em seu computador.\n")
            f.write("echo.\n")
            f.write("set DEFAULT_DIR=" + config["diretorio_instalacao_padrao"]["windows"] + "\n")
            f.write("set /p INSTALL_DIR=Digite o diretorio de instalacao ou pressione ENTER para usar o padrao [%DEFAULT_DIR%]: \n")
            f.write("if \"%INSTALL_DIR%\"==\"\" set INSTALL_DIR=%DEFAULT_DIR%\n")
            f.write("echo.\n")
            f.write("echo Instalando em %INSTALL_DIR%...\n")
            f.write("echo.\n")
            f.write("if not exist \"%INSTALL_DIR%\" mkdir \"%INSTALL_DIR%\"\n")
            f.write("xcopy /E /I /Y files\\* \"%INSTALL_DIR%\"\n")
            f.write("echo.\n")
            f.write("echo Verificando requisitos...\n")
            f.write("python --version > nul 2>&1\n")
            f.write("if %ERRORLEVEL% neq 0 (\n")
            f.write("    echo ERRO: Python nao encontrado. Por favor, instale o Python " + config["requisitos_sistema"]["python_minimo"] + " ou superior.\n")
            f.write("    pause\n")
            f.write("    exit /b 1\n")
            f.write(")\n")
            f.write("echo Instalando dependencias...\n")
            f.write("pip install -r \"%INSTALL_DIR%\\requirements.txt\"\n")
            f.write("echo.\n")
            if config["criar_atalhos"]:
                f.write("echo Criando atalhos...\n")
                f.write("echo @echo off > \"%INSTALL_DIR%\\start.bat\"\n")
                f.write("echo cd /d \"%INSTALL_DIR%\" >> \"%INSTALL_DIR%\\start.bat\"\n")
                f.write("echo python src\\main.py >> \"%INSTALL_DIR%\\start.bat\"\n")
                f.write("echo.\n")
            if config["criar_desinstalador"]:
                f.write("echo Criando desinstalador...\n")
                f.write("echo @echo off > \"%INSTALL_DIR%\\uninstall.bat\"\n")
                f.write("echo echo Desinstalando " + config["nome_aplicacao"] + "... >> \"%INSTALL_DIR%\\uninstall.bat\"\n")
                f.write("echo rmdir /S /Q \"%INSTALL_DIR%\" >> \"%INSTALL_DIR%\\uninstall.bat\"\n")
                f.write("echo.\n")
            f.write("echo Instalacao concluida com sucesso!\n")
            f.write("echo.\n")
            f.write("echo Para iniciar o aplicativo, execute %INSTALL_DIR%\\start.bat\n")
            f.write("echo.\n")
            f.write("pause\n")
        
        # Criar script de instalação para Linux/Mac
        script_unix = os.path.join(destino, "install.sh")
        with open(script_unix, 'w', newline='\n') as f:
            f.write("#!/bin/bash\n")
            f.write("echo \"Instalador do " + config["nome_aplicacao"] + " " + config["versao"] + "\"\n")
            f.write("echo\n")
            f.write("echo \"Este instalador configurará o software " + config["nome_aplicacao"] + " em seu computador.\"\n")
            f.write("echo\n")
            f.write("# Detectar sistema operacional\n")
            f.write("OS=$(uname -s)\n")
            f.write("if [ \"$OS\" = \"Darwin\" ]; then\n")
            f.write("    DEFAULT_DIR=\"" + config["diretorio_instalacao_padrao"]["darwin"] + "\"\n")
            f.write("else\n")
            f.write("    DEFAULT_DIR=\"" + config["diretorio_instalacao_padrao"]["linux"] + "\"\n")
            f.write("fi\n")
            f.write("read -p \"Digite o diretório de instalação ou pressione ENTER para usar o padrão [$DEFAULT_DIR]: \" INSTALL_DIR\n")
            f.write("INSTALL_DIR=${INSTALL_DIR:-$DEFAULT_DIR}\n")
            f.write("echo\n")
            f.write("echo \"Instalando em $INSTALL_DIR...\"\n")
            f.write("echo\n")
            f.write("mkdir -p \"$INSTALL_DIR\"\n")
            f.write("cp -R files/* \"$INSTALL_DIR\"\n")
            f.write("echo\n")
            f.write("echo \"Verificando requisitos...\"\n")
            f.write("if ! command -v python3 &> /dev/null; then\n")
            f.write("    echo \"ERRO: Python não encontrado. Por favor, instale o Python " + config["requisitos_sistema"]["python_minimo"] + " ou superior.\"\n")
            f.write("    exit 1\n")
            f.write("fi\n")
            f.write("echo \"Instalando dependências...\"\n")
            f.write("pip3 install -r \"$INSTALL_DIR/requirements.txt\"\n")
            f.write("echo\n")
            if config["criar_atalhos"]:
                f.write("echo \"Criando atalhos...\"\n")
                f.write("echo '#!/bin/bash' > \"$INSTALL_DIR/start.sh\"\n")
                f.write("echo 'cd \"$INSTALL_DIR\"' >> \"$INSTALL_DIR/start.sh\"\n")
                f.write("echo 'python3 src/main.py' >> \"$INSTALL_DIR/start.sh\"\n")
                f.write("chmod +x \"$INSTALL_DIR/start.sh\"\n")
                f.write("echo\n")
            if config["criar_desinstalador"]:
                f.write("echo \"Criando desinstalador...\"\n")
                f.write("echo '#!/bin/bash' > \"$INSTALL_DIR/uninstall.sh\"\n")
                f.write("echo 'echo \"Desinstalando " + config["nome_aplicacao"] + "...\"' >> \"$INSTALL_DIR/uninstall.sh\"\n")
                f.write("echo 'rm -rf \"$INSTALL_DIR\"' >> \"$INSTALL_DIR/uninstall.sh\"\n")
                f.write("chmod +x \"$INSTALL_DIR/uninstall.sh\"\n")
                f.write("echo\n")
            f.write("echo \"Instalação concluída com sucesso!\"\n")
            f.write("echo\n")
            f.write("echo \"Para iniciar o aplicativo, execute $INSTALL_DIR/start.sh\"\n")
            f.write("echo\n")
            f.write("read -p \"Pressione ENTER para continuar...\"\n")
        
        # Tornar o script Unix executável
        os.chmod(script_unix, 0o755)
    
    def desinstalar(self):
        """
        Desinstala o software.
        
        Returns:
            dict: Resultado da operação
        """
        logger.info("Desinstalando software...")
        
        try:
            # Verificar se está sendo executado do diretório de instalação
            if not os.path.exists(os.path.join(self.diretorio_base, "src", "main.py")):
                return {
                    "sucesso": False,
                    "mensagem": "Este comando deve ser executado do diretório de instalação"
                }
            
            # Confirmar desinstalação
            print("ATENÇÃO: Esta operação removerá todos os arquivos do software.")
            print("Diretório a ser removido:", self.diretorio_base)
            confirmacao = input("Digite 'SIM' para confirmar a desinstalação: ")
            
            if confirmacao != "SIM":
                return {
                    "sucesso": False,
                    "mensagem": "Desinstalação cancelada pelo usuário"
                }
            
            # Criar backup antes de desinstalar
            from manutencao.backup import SistemaBackup
            sistema_backup = SistemaBackup()
            backup = sistema_backup.criar_backup("Backup pré-desinstalação")
            
            if not backup:
                print("Aviso: Não foi possível criar backup antes da desinstalação.")
            else:
                print(f"Backup criado em: {backup}")
            
            # Remover diretório de instalação
            # Não remover o diretório atual para evitar erros
            # Em vez disso, listar e remover os arquivos e diretórios individualmente
            for item in os.listdir(self.diretorio_base):
                # Pular o diretório de backup se existir
                if item == "backups":
                    continue
                
                caminho = os.path.join(self.diretorio_base, item)
                
                if os.path.isdir(caminho):
                    shutil.rmtree(caminho)
                else:
                    os.remove(caminho)
            
            logger.info("Software desinstalado com sucesso")
            return {
                "sucesso": True,
                "mensagem": "Software desinstalado com sucesso",
                "backup": backup
            }
            
        except Exception as e:
            logger.error(f"Erro ao desinstalar software: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao desinstalar software: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def verificar_requisitos_sistema(self):
        """
        Verifica se o sistema atende aos requisitos mínimos.
        
        Returns:
            dict: Resultado da verificação
        """
        logger.info("Verificando requisitos do sistema...")
        
        try:
            # Carregar configuração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            requisitos = config["requisitos_sistema"]
            
            resultado = {
                "atende_requisitos": True,
                "detalhes": {}
            }
            
            # Verificar versão do Python
            python_atual = platform.python_version()
            python_minimo = requisitos["python_minimo"]
            
            resultado["detalhes"]["python"] = {
                "atual": python_atual,
                "minimo": python_minimo,
                "atende": self._comparar_versoes(python_atual, python_minimo)
            }
            
            if not resultado["detalhes"]["python"]["atende"]:
                resultado["atende_requisitos"] = False
            
            # Verificar espaço em disco
            import psutil
            
            disco_total = psutil.disk_usage(self.diretorio_base).total / (1024 * 1024)  # MB
            disco_livre = psutil.disk_usage(self.diretorio_base).free / (1024 * 1024)  # MB
            disco_minimo = requisitos["espaco_disco_mb"]
            
            resultado["detalhes"]["disco"] = {
                "total_mb": round(disco_total, 2),
                "livre_mb": round(disco_livre, 2),
                "minimo_mb": disco_minimo,
                "atende": disco_livre >= disco_minimo
            }
            
            if not resultado["detalhes"]["disco"]["atende"]:
                resultado["atende_requisitos"] = False
            
            # Verificar memória
            memoria_total = psutil.virtual_memory().total / (1024 * 1024)  # MB
            memoria_minima = requisitos["memoria_mb"]
            
            resultado["detalhes"]["memoria"] = {
                "total_mb": round(memoria_total, 2),
                "minima_mb": memoria_minima,
                "atende": memoria_total >= memoria_minima
            }
            
            if not resultado["detalhes"]["memoria"]["atende"]:
                resultado["atende_requisitos"] = False
            
            logger.info(f"Verificação de requisitos concluída: {resultado['atende_requisitos']}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao verificar requisitos do sistema: {str(e)}")
            return {
                "atende_requisitos": False,
                "erro": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _comparar_versoes(self, versao_atual, versao_minima):
        """
        Compara duas versões no formato X.Y.Z.
        
        Args:
            versao_atual: Versão atual
            versao_minima: Versão mínima
            
        Returns:
            bool: True se a versão atual for maior ou igual à mínima
        """
        def normalizar_versao(versao):
            return [int(x) for x in versao.split('.')]
        
        atual = normalizar_versao(versao_atual)
        minima = normalizar_versao(versao_minima)
        
        # Garantir que ambas as listas tenham o mesmo tamanho
        while len(atual) < len(minima):
            atual.append(0)
        
        while len(minima) < len(atual):
            minima.append(0)
        
        # Comparar componentes
        for a, m in zip(atual, minima):
            if a > m:
                return True
            elif a < m:
                return False
        
        # Se chegou aqui, são iguais
        return True

# Adicionar rotas para o sistema de instalação
def adicionar_rotas_instalador(app):
    """
    Adiciona rotas para o sistema de instalação à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify, send_file
    
    @app.route('/manutencao/instalador')
    def pagina_instalador():
        sistema_instalador = SistemaInstalador()
        
        # Carregar configuração
        with open(sistema_instalador.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar requisitos
        requisitos = sistema_instalador.verificar_requisitos_sistema()
        
        return jsonify({
            "configuracoes": config,
            "requisitos_sistema": requisitos
        })
    
    @app.route('/manutencao/instalador/criar_pacote', methods=['POST'])
    def criar_pacote_instalacao():
        sistema_instalador = SistemaInstalador()
        
        resultado = sistema_instalador.criar_pacote_instalacao()
        
        if resultado["sucesso"]:
            return jsonify({
                "sucesso": True,
                "mensagem": resultado["mensagem"],
                "caminho": resultado["caminho"]
            })
        else:
            return jsonify({
                "sucesso": False,
                "mensagem": resultado["mensagem"]
            })
    
    @app.route('/manutencao/instalador/download/<nome_arquivo>')
    def download_instalador(nome_arquivo):
        sistema_instalador = SistemaInstalador()
        
        caminho = os.path.join(sistema_instalador.diretorio_instalador, nome_arquivo)
        
        if not os.path.exists(caminho):
            return jsonify({
                "sucesso": False,
                "mensagem": "Arquivo não encontrado"
            })
        
        return send_file(caminho, as_attachment=True)
    
    @app.route('/manutencao/instalador/configuracoes', methods=['POST'])
    def atualizar_configuracoes_instalador():
        try:
            sistema_instalador = SistemaInstalador()
            
            # Carregar configuração atual
            with open(sistema_instalador.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Atualizar configurações
            dados = request.json
            
            # Campos permitidos para atualização
            campos_permitidos = [
                "versao", "nome_aplicacao", "empresa", "autor", "website",
                "diretorio_instalacao_padrao", "arquivos_essenciais",
                "criar_atalhos", "criar_menu_iniciar", "criar_desinstalador",
                "requisitos_sistema"
            ]
            
            for campo in campos_permitidos:
                if campo in dados:
                    config[campo] = dados[campo]
            
            # Salvar configuração
            with open(sistema_instalador.arquivo_config, 'w', encoding='utf-8') as f:
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
