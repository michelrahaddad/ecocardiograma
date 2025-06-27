"""
Módulo de Gerenciamento de Usuários

Este módulo implementa um sistema de gerenciamento de usuários para o software de ecocardiograma.
Permite criar, editar, excluir e gerenciar permissões de usuários do sistema.
"""

import os
import json
import sqlite3
import logging
import hashlib
import secrets
import time
import datetime
import traceback
from functools import wraps
from flask import session, redirect, url_for, request, flash

# Configuração do logger
logger = logging.getLogger('sistema_usuarios')

class SistemaUsuarios:
    def __init__(self):
        """
        Inicializa o sistema de gerenciamento de usuários.
        """
        self.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arquivo_config = os.path.join(self.diretorio_base, "config", "usuarios.json")
        self.arquivo_db = os.path.join(self.diretorio_base, "ecocardiograma.db")
        
        # Criar diretórios necessários
        os.makedirs(os.path.join(self.diretorio_base, "config"), exist_ok=True)
        
        # Inicializar configuração
        self._inicializar_config()
        
        # Configurar logger
        self._configurar_logger()
        
        # Inicializar banco de dados
        self._inicializar_db()
    
    def _configurar_logger(self):
        """Configura o sistema de logs para o módulo de usuários."""
        log_dir = os.path.join(self.diretorio_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "usuarios.log")
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    
    def _inicializar_config(self):
        """Inicializa o arquivo de configuração de usuários."""
        if not os.path.exists(self.arquivo_config):
            config = {
                "politica_senha": {
                    "tamanho_minimo": 8,
                    "requer_maiuscula": True,
                    "requer_minuscula": True,
                    "requer_numero": True,
                    "requer_especial": True,
                    "max_dias_validade": 90
                },
                "bloqueio_conta": {
                    "max_tentativas": 5,
                    "tempo_bloqueio_minutos": 30
                },
                "sessao": {
                    "tempo_expiracao_minutos": 30,
                    "permitir_multiplas_sessoes": False
                },
                "perfis": {
                    "administrador": {
                        "descricao": "Acesso total ao sistema",
                        "permissoes": ["*"]
                    },
                    "medico": {
                        "descricao": "Médico que realiza exames",
                        "permissoes": ["exames.*", "laudos.*", "parametros.*", "modelos_laudo.ler"]
                    },
                    "assistente": {
                        "descricao": "Assistente que cadastra pacientes e exames",
                        "permissoes": ["exames.criar", "exames.ler", "exames.editar", "parametros.criar", "parametros.ler"]
                    }
                }
            }
            
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            logger.info("Arquivo de configuração de usuários criado")
    
    def _inicializar_db(self):
        """Inicializa o banco de dados para gerenciamento de usuários."""
        conn = sqlite3.connect(self.arquivo_db)
        cursor = conn.cursor()
        
        # Criar tabela de usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            email TEXT,
            perfil TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            tentativas_login INTEGER DEFAULT 0,
            bloqueado_ate TEXT,
            ultimo_login TEXT,
            data_criacao TEXT NOT NULL,
            data_modificacao TEXT NOT NULL,
            data_expiracao_senha TEXT,
            permissoes_personalizadas TEXT
        )
        ''')
        
        # Criar tabela de logs de acesso
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_acesso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            data TEXT NOT NULL,
            ip TEXT,
            acao TEXT NOT NULL,
            detalhes TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        ''')
        
        # Criar índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_login ON usuarios (login)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_acesso_usuario ON logs_acesso (usuario_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_acesso_data ON logs_acesso (data)')
        
        conn.commit()
        
        # Verificar se existe um usuário administrador
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE perfil = "administrador"')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Criar usuário administrador padrão
            agora = datetime.datetime.now().isoformat()
            
            # Gerar senha aleatória
            senha_admin = secrets.token_urlsafe(12)
            senha_hash = self._hash_senha("admin123")
            
            cursor.execute('''
            INSERT INTO usuarios (nome, login, senha_hash, email, perfil, ativo, data_criacao, data_modificacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("Administrador", "admin", senha_hash, "admin@sistema.local", "administrador", 1, agora, agora))
            
            conn.commit()
            
            logger.info(f"Usuário administrador criado com senha: admin123")
        
        conn.close()
    
    def _hash_senha(self, senha):
        """
        Gera um hash seguro para a senha.
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            str: Hash da senha
        """
        # Usar SHA-256 para o hash
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def _verificar_politica_senha(self, senha):
        """
        Verifica se a senha atende à política de segurança.
        
        Args:
            senha: Senha a verificar
            
        Returns:
            tuple: (bool, str) - Válida e mensagem
        """
        with open(self.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        politica = config["politica_senha"]
        
        # Verificar tamanho mínimo
        if len(senha) < politica["tamanho_minimo"]:
            return False, f"A senha deve ter pelo menos {politica['tamanho_minimo']} caracteres"
        
        # Verificar requisitos de caracteres
        if politica["requer_maiuscula"] and not any(c.isupper() for c in senha):
            return False, "A senha deve conter pelo menos uma letra maiúscula"
        
        if politica["requer_minuscula"] and not any(c.islower() for c in senha):
            return False, "A senha deve conter pelo menos uma letra minúscula"
        
        if politica["requer_numero"] and not any(c.isdigit() for c in senha):
            return False, "A senha deve conter pelo menos um número"
        
        if politica["requer_especial"] and not any(not c.isalnum() for c in senha):
            return False, "A senha deve conter pelo menos um caractere especial"
        
        return True, "Senha válida"
    
    def criar_usuario(self, nome, login, senha, email, perfil):
        """
        Cria um novo usuário.
        
        Args:
            nome: Nome completo do usuário
            login: Nome de usuário para login
            senha: Senha em texto plano
            email: Email do usuário
            perfil: Perfil de acesso
            
        Returns:
            dict: Resultado da operação
        """
        logger.info(f"Criando usuário: {login}")
        
        try:
            # Verificar política de senha
            senha_valida, mensagem = self._verificar_politica_senha(senha)
            if not senha_valida:
                return {
                    "sucesso": False,
                    "mensagem": mensagem
                }
            
            # Verificar se o perfil existe
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if perfil not in config["perfis"]:
                return {
                    "sucesso": False,
                    "mensagem": f"Perfil '{perfil}' não existe"
                }
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar se o login já existe
            cursor.execute('SELECT id FROM usuarios WHERE login = ?', (login,))
            if cursor.fetchone():
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": f"Login '{login}' já está em uso"
                }
            
            # Gerar hash da senha
            senha_hash = self._hash_senha(senha)
            
            # Data atual
            agora = datetime.datetime.now().isoformat()
            
            # Calcular data de expiração da senha
            data_expiracao = None
            if config["politica_senha"]["max_dias_validade"] > 0:
                data_expiracao = (datetime.datetime.now() + datetime.timedelta(days=config["politica_senha"]["max_dias_validade"])).isoformat()
            
            # Inserir usuário
            cursor.execute('''
            INSERT INTO usuarios (
                nome, login, senha_hash, email, perfil, ativo, 
                data_criacao, data_modificacao, data_expiracao_senha
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, login, senha_hash, email, perfil, 1, agora, agora, data_expiracao))
            
            usuario_id = cursor.lastrowid
            
            # Registrar log
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, acao, detalhes)
            VALUES (?, ?, ?, ?)
            ''', (None, agora, "criar_usuario", json.dumps({
                "usuario_id": usuario_id,
                "login": login,
                "perfil": perfil
            })))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuário '{login}' criado com sucesso")
            return {
                "sucesso": True,
                "mensagem": f"Usuário '{login}' criado com sucesso",
                "usuario_id": usuario_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao criar usuário: {str(e)}"
            }
    
    def autenticar_usuario(self, login, senha, ip=None):
        """
        Autentica um usuário.
        
        Args:
            login: Nome de usuário
            senha: Senha em texto plano
            ip: Endereço IP do usuário
            
        Returns:
            dict: Resultado da autenticação
        """
        logger.info(f"Tentativa de login: {login}")
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute('SELECT * FROM usuarios WHERE login = ?', (login,))
            usuario = cursor.fetchone()
            
            # Data atual
            agora = datetime.datetime.now()
            agora_iso = agora.isoformat()
            
            # Verificar se o usuário existe
            if not usuario:
                # Registrar tentativa de login inválida
                cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
                VALUES (?, ?, ?, ?, ?)
                ''', (None, agora_iso, ip, "login_falha", json.dumps({
                    "motivo": "usuario_inexistente",
                    "login": login
                })))
                
                conn.commit()
                conn.close()
                
                logger.warning(f"Tentativa de login com usuário inexistente: {login}")
                return {
                    "sucesso": False,
                    "mensagem": "Usuário ou senha inválidos"
                }
            
            # Verificar se o usuário está ativo
            if not usuario["ativo"]:
                # Registrar tentativa de login em conta inativa
                cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
                VALUES (?, ?, ?, ?, ?)
                ''', (usuario["id"], agora_iso, ip, "login_falha", json.dumps({
                    "motivo": "conta_inativa",
                    "login": login
                })))
                
                conn.commit()
                conn.close()
                
                logger.warning(f"Tentativa de login em conta inativa: {login}")
                return {
                    "sucesso": False,
                    "mensagem": "Conta inativa. Entre em contato com o administrador."
                }
            
            # Verificar se a conta está bloqueada
            if usuario["bloqueado_ate"]:
                data_bloqueio = datetime.datetime.fromisoformat(usuario["bloqueado_ate"])
                
                if agora < data_bloqueio:
                    # Conta ainda bloqueada
                    tempo_restante = data_bloqueio - agora
                    minutos_restantes = int(tempo_restante.total_seconds() / 60)
                    
                    # Registrar tentativa de login em conta bloqueada
                    cursor.execute('''
                    INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (usuario["id"], agora_iso, ip, "login_falha", json.dumps({
                        "motivo": "conta_bloqueada",
                        "login": login,
                        "bloqueado_ate": usuario["bloqueado_ate"]
                    })))
                    
                    conn.commit()
                    conn.close()
                    
                    logger.warning(f"Tentativa de login em conta bloqueada: {login}")
                    return {
                        "sucesso": False,
                        "mensagem": f"Conta bloqueada. Tente novamente em {minutos_restantes} minutos."
                    }
                else:
                    # Desbloquear conta
                    cursor.execute('''
                    UPDATE usuarios SET bloqueado_ate = NULL, tentativas_login = 0
                    WHERE id = ?
                    ''', (usuario["id"],))
            
            # Verificar senha
            senha_hash = self._hash_senha(senha)
            
            if senha_hash != usuario["senha_hash"]:
                # Incrementar contador de tentativas
                with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                max_tentativas = config["bloqueio_conta"]["max_tentativas"]
                tempo_bloqueio = config["bloqueio_conta"]["tempo_bloqueio_minutos"]
                
                tentativas = usuario["tentativas_login"] + 1
                
                if tentativas >= max_tentativas:
                    # Bloquear conta
                    data_bloqueio = (agora + datetime.timedelta(minutes=tempo_bloqueio)).isoformat()
                    
                    cursor.execute('''
                    UPDATE usuarios SET tentativas_login = ?, bloqueado_ate = ?
                    WHERE id = ?
                    ''', (tentativas, data_bloqueio, usuario["id"]))
                    
                    # Registrar bloqueio
                    cursor.execute('''
                    INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (usuario["id"], agora_iso, ip, "conta_bloqueada", json.dumps({
                        "motivo": "excesso_tentativas",
                        "tentativas": tentativas,
                        "bloqueado_ate": data_bloqueio
                    })))
                    
                    mensagem_erro = f"Conta bloqueada por {tempo_bloqueio} minutos devido a múltiplas tentativas de login."
                else:
                    # Atualizar contador de tentativas
                    cursor.execute('''
                    UPDATE usuarios SET tentativas_login = ?
                    WHERE id = ?
                    ''', (tentativas, usuario["id"]))
                    
                    tentativas_restantes = max_tentativas - tentativas
                    mensagem_erro = f"Usuário ou senha inválidos. Tentativas restantes: {tentativas_restantes}"
                
                # Registrar falha de login
                cursor.execute('''
                INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
                VALUES (?, ?, ?, ?, ?)
                ''', (usuario["id"], agora_iso, ip, "login_falha", json.dumps({
                    "motivo": "senha_invalida",
                    "login": login,
                    "tentativas": tentativas
                })))
                
                conn.commit()
                conn.close()
                
                logger.warning(f"Tentativa de login com senha inválida: {login} (tentativa {tentativas})")
                return {
                    "sucesso": False,
                    "mensagem": mensagem_erro
                }
            
            # Verificar expiração de senha
            senha_expirada = False
            if usuario["data_expiracao_senha"]:
                data_expiracao = datetime.datetime.fromisoformat(usuario["data_expiracao_senha"])
                if agora > data_expiracao:
                    senha_expirada = True
            
            # Login bem-sucedido
            cursor.execute('''
            UPDATE usuarios SET tentativas_login = 0, ultimo_login = ?
            WHERE id = ?
            ''', (agora_iso, usuario["id"]))
            
            # Registrar login bem-sucedido
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
            VALUES (?, ?, ?, ?, ?)
            ''', (usuario["id"], agora_iso, ip, "login_sucesso", json.dumps({
                "login": login
            })))
            
            conn.commit()
            
            # Buscar permissões
            permissoes = self._obter_permissoes_usuario(usuario["id"], usuario["perfil"], conn)
            
            conn.close()
            
            logger.info(f"Login bem-sucedido: {login}")
            return {
                "sucesso": True,
                "mensagem": "Login bem-sucedido",
                "usuario": {
                    "id": usuario["id"],
                    "nome": usuario["nome"],
                    "login": usuario["login"],
                    "email": usuario["email"],
                    "perfil": usuario["perfil"],
                    "permissoes": permissoes,
                    "senha_expirada": senha_expirada
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao autenticar usuário: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao autenticar usuário: {str(e)}"
            }
    
    def _obter_permissoes_usuario(self, usuario_id, perfil, conn=None):
        """
        Obtém as permissões de um usuário.
        
        Args:
            usuario_id: ID do usuário
            perfil: Perfil do usuário
            conn: Conexão com o banco de dados (opcional)
            
        Returns:
            list: Lista de permissões
        """
        # Carregar configuração
        with open(self.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Obter permissões do perfil
        permissoes_perfil = []
        if perfil in config["perfis"]:
            permissoes_perfil = config["perfis"][perfil]["permissoes"]
        
        # Verificar se há permissões personalizadas
        permissoes_personalizadas = []
        
        fechar_conexao = False
        if conn is None:
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            fechar_conexao = True
        
        cursor = conn.cursor()
        
        cursor.execute('SELECT permissoes_personalizadas FROM usuarios WHERE id = ?', (usuario_id,))
        resultado = cursor.fetchone()
        
        if resultado and resultado["permissoes_personalizadas"]:
            try:
                permissoes_personalizadas = json.loads(resultado["permissoes_personalizadas"])
            except:
                pass
        
        if fechar_conexao:
            conn.close()
        
        # Combinar permissões
        permissoes = permissoes_perfil + permissoes_personalizadas
        
        # Remover duplicatas
        return list(set(permissoes))
    
    def alterar_senha(self, usuario_id, senha_atual, nova_senha):
        """
        Altera a senha de um usuário.
        
        Args:
            usuario_id: ID do usuário
            senha_atual: Senha atual
            nova_senha: Nova senha
            
        Returns:
            dict: Resultado da operação
        """
        logger.info(f"Alterando senha do usuário ID: {usuario_id}")
        
        try:
            # Verificar política de senha
            senha_valida, mensagem = self._verificar_politica_senha(nova_senha)
            if not senha_valida:
                return {
                    "sucesso": False,
                    "mensagem": mensagem
                }
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado"
                }
            
            # Verificar senha atual
            senha_hash_atual = self._hash_senha(senha_atual)
            
            if senha_hash_atual != usuario["senha_hash"]:
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Senha atual incorreta"
                }
            
            # Gerar hash da nova senha
            senha_hash_nova = self._hash_senha(nova_senha)
            
            # Data atual
            agora = datetime.datetime.now().isoformat()
            
            # Calcular nova data de expiração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            data_expiracao = None
            if config["politica_senha"]["max_dias_validade"] > 0:
                data_expiracao = (datetime.datetime.now() + datetime.timedelta(days=config["politica_senha"]["max_dias_validade"])).isoformat()
            
            # Atualizar senha
            cursor.execute('''
            UPDATE usuarios SET 
                senha_hash = ?, 
                data_modificacao = ?,
                data_expiracao_senha = ?
            WHERE id = ?
            ''', (senha_hash_nova, agora, data_expiracao, usuario_id))
            
            # Registrar alteração
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, acao, detalhes)
            VALUES (?, ?, ?, ?)
            ''', (usuario_id, agora, "alterar_senha", json.dumps({
                "usuario_id": usuario_id
            })))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Senha alterada com sucesso para o usuário ID: {usuario_id}")
            return {
                "sucesso": True,
                "mensagem": "Senha alterada com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao alterar senha: {str(e)}"
            }
    
    def redefinir_senha(self, usuario_id, nova_senha=None):
        """
        Redefine a senha de um usuário (função administrativa).
        
        Args:
            usuario_id: ID do usuário
            nova_senha: Nova senha (opcional, gera uma aleatória se não fornecida)
            
        Returns:
            dict: Resultado da operação
        """
        logger.info(f"Redefinindo senha do usuário ID: {usuario_id}")
        
        try:
            # Gerar senha aleatória se não fornecida
            if not nova_senha:
                nova_senha = secrets.token_urlsafe(12)
            else:
                # Verificar política de senha
                senha_valida, mensagem = self._verificar_politica_senha(nova_senha)
                if not senha_valida:
                    return {
                        "sucesso": False,
                        "mensagem": mensagem
                    }
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar se o usuário existe
            cursor.execute('SELECT id FROM usuarios WHERE id = ?', (usuario_id,))
            if not cursor.fetchone():
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado"
                }
            
            # Gerar hash da nova senha
            senha_hash = self._hash_senha(nova_senha)
            
            # Data atual
            agora = datetime.datetime.now().isoformat()
            
            # Calcular nova data de expiração
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            data_expiracao = None
            if config["politica_senha"]["max_dias_validade"] > 0:
                data_expiracao = (datetime.datetime.now() + datetime.timedelta(days=config["politica_senha"]["max_dias_validade"])).isoformat()
            
            # Atualizar senha e desbloquear conta
            cursor.execute('''
            UPDATE usuarios SET 
                senha_hash = ?, 
                data_modificacao = ?,
                data_expiracao_senha = ?,
                tentativas_login = 0,
                bloqueado_ate = NULL
            WHERE id = ?
            ''', (senha_hash, agora, data_expiracao, usuario_id))
            
            # Registrar redefinição
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, acao, detalhes)
            VALUES (?, ?, ?, ?)
            ''', (None, agora, "redefinir_senha", json.dumps({
                "usuario_id": usuario_id,
                "admin_id": session.get("usuario_id") if hasattr(session, "usuario_id") else None
            })))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Senha redefinida com sucesso para o usuário ID: {usuario_id}")
            return {
                "sucesso": True,
                "mensagem": "Senha redefinida com sucesso",
                "nova_senha": nova_senha
            }
            
        except Exception as e:
            logger.error(f"Erro ao redefinir senha: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao redefinir senha: {str(e)}"
            }
    
    def atualizar_usuario(self, usuario_id, dados):
        """
        Atualiza os dados de um usuário.
        
        Args:
            usuario_id: ID do usuário
            dados: Dicionário com os dados a atualizar
            
        Returns:
            dict: Resultado da operação
        """
        logger.info(f"Atualizando usuário ID: {usuario_id}")
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar se o usuário existe
            cursor.execute('SELECT id FROM usuarios WHERE id = ?', (usuario_id,))
            if not cursor.fetchone():
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado"
                }
            
            # Campos permitidos para atualização
            campos_permitidos = ["nome", "email", "perfil", "ativo", "permissoes_personalizadas"]
            
            # Construir query de atualização
            campos = []
            valores = []
            
            for campo, valor in dados.items():
                if campo in campos_permitidos:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Nenhum campo válido para atualização"
                }
            
            # Adicionar data de modificação
            campos.append("data_modificacao = ?")
            valores.append(datetime.datetime.now().isoformat())
            
            # Adicionar ID do usuário
            valores.append(usuario_id)
            
            # Executar atualização
            query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            
            # Registrar atualização
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, acao, detalhes)
            VALUES (?, ?, ?, ?)
            ''', (session.get("usuario_id") if hasattr(session, "usuario_id") else None, 
                 datetime.datetime.now().isoformat(), 
                 "atualizar_usuario", 
                 json.dumps({
                     "usuario_id": usuario_id,
                     "campos_atualizados": list(dados.keys())
                 })))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuário ID: {usuario_id} atualizado com sucesso")
            return {
                "sucesso": True,
                "mensagem": "Usuário atualizado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao atualizar usuário: {str(e)}"
            }
    
    def excluir_usuario(self, usuario_id):
        """
        Exclui um usuário.
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            dict: Resultado da operação
        """
        logger.info(f"Excluindo usuário ID: {usuario_id}")
        
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            cursor = conn.cursor()
            
            # Verificar se o usuário existe
            cursor.execute('SELECT id, login FROM usuarios WHERE id = ?', (usuario_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Usuário não encontrado"
                }
            
            # Verificar se não é o último administrador
            cursor.execute('SELECT COUNT(*) FROM usuarios WHERE perfil = "administrador" AND id != ?', (usuario_id,))
            count_admin = cursor.fetchone()[0]
            
            cursor.execute('SELECT perfil FROM usuarios WHERE id = ?', (usuario_id,))
            perfil = cursor.fetchone()[0]
            
            if perfil == "administrador" and count_admin == 0:
                conn.close()
                return {
                    "sucesso": False,
                    "mensagem": "Não é possível excluir o último administrador do sistema"
                }
            
            # Excluir usuário
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            
            # Registrar exclusão
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, acao, detalhes)
            VALUES (?, ?, ?, ?)
            ''', (session.get("usuario_id") if hasattr(session, "usuario_id") else None, 
                 datetime.datetime.now().isoformat(), 
                 "excluir_usuario", 
                 json.dumps({
                     "usuario_id": usuario_id,
                     "login": usuario[1]
                 })))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuário ID: {usuario_id} excluído com sucesso")
            return {
                "sucesso": True,
                "mensagem": "Usuário excluído com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao excluir usuário: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": f"Erro ao excluir usuário: {str(e)}"
            }
    
    def listar_usuarios(self):
        """
        Lista todos os usuários.
        
        Returns:
            list: Lista de usuários
        """
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuários
            cursor.execute('''
            SELECT id, nome, login, email, perfil, ativo, ultimo_login, data_criacao, data_modificacao
            FROM usuarios
            ORDER BY nome
            ''')
            
            usuarios = []
            for row in cursor.fetchall():
                usuarios.append(dict(row))
            
            conn.close()
            
            return usuarios
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {str(e)}")
            return []
    
    def obter_usuario(self, usuario_id):
        """
        Obtém os dados de um usuário.
        
        Args:
            usuario_id: ID do usuário
            
        Returns:
            dict: Dados do usuário ou None
        """
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute('''
            SELECT id, nome, login, email, perfil, ativo, ultimo_login, 
                   data_criacao, data_modificacao, data_expiracao_senha,
                   permissoes_personalizadas
            FROM usuarios
            WHERE id = ?
            ''', (usuario_id,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                conn.close()
                return None
            
            # Converter para dicionário
            resultado = dict(usuario)
            
            # Obter permissões
            resultado["permissoes"] = self._obter_permissoes_usuario(usuario_id, resultado["perfil"], conn)
            
            conn.close()
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {str(e)}")
            return None
    
    def verificar_permissao(self, usuario_id, permissao):
        """
        Verifica se um usuário tem uma determinada permissão.
        
        Args:
            usuario_id: ID do usuário
            permissao: Permissão a verificar
            
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar perfil do usuário
            cursor.execute('SELECT perfil FROM usuarios WHERE id = ?', (usuario_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return False
            
            perfil = resultado["perfil"]
            
            # Obter permissões
            permissoes = self._obter_permissoes_usuario(usuario_id, perfil, conn)
            
            conn.close()
            
            # Verificar permissão coringa
            if "*" in permissoes:
                return True
            
            # Verificar permissão específica
            if permissao in permissoes:
                return True
            
            # Verificar permissão por categoria
            partes = permissao.split('.')
            if len(partes) > 1:
                permissao_categoria = f"{partes[0]}.*"
                if permissao_categoria in permissoes:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar permissão: {str(e)}")
            return False
    
    def obter_logs_acesso(self, filtros=None, limite=100):
        """
        Obtém logs de acesso.
        
        Args:
            filtros: Dicionário com filtros
            limite: Limite de resultados
            
        Returns:
            list: Lista de logs
        """
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.arquivo_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Construir query
            query = '''
            SELECT l.id, l.usuario_id, u.login, l.data, l.ip, l.acao, l.detalhes
            FROM logs_acesso l
            LEFT JOIN usuarios u ON l.usuario_id = u.id
            WHERE 1=1
            '''
            
            params = []
            
            if filtros:
                if "usuario_id" in filtros:
                    query += " AND l.usuario_id = ?"
                    params.append(filtros["usuario_id"])
                
                if "acao" in filtros:
                    query += " AND l.acao = ?"
                    params.append(filtros["acao"])
                
                if "data_inicio" in filtros:
                    query += " AND l.data >= ?"
                    params.append(filtros["data_inicio"])
                
                if "data_fim" in filtros:
                    query += " AND l.data <= ?"
                    params.append(filtros["data_fim"])
            
            query += " ORDER BY l.data DESC LIMIT ?"
            params.append(limite)
            
            # Executar query
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                log = dict(row)
                
                # Converter detalhes JSON
                if log["detalhes"]:
                    try:
                        log["detalhes"] = json.loads(log["detalhes"])
                    except:
                        pass
                
                logs.append(log)
            
            conn.close()
            
            return logs
            
        except Exception as e:
            logger.error(f"Erro ao obter logs de acesso: {str(e)}")
            return []

# Decorador para verificar autenticação
def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Você precisa fazer login para acessar esta página.", "danger")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar permissão
def requer_permissao(permissao):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "usuario_id" not in session:
                flash("Você precisa fazer login para acessar esta página.", "danger")
                return redirect(url_for("login", next=request.url))
            
            sistema_usuarios = SistemaUsuarios()
            if not sistema_usuarios.verificar_permissao(session["usuario_id"], permissao):
                flash("Você não tem permissão para acessar esta página.", "danger")
                return redirect(url_for("index"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Função para integração com a aplicação principal
def configurar_autenticacao(app):
    """
    Configura o sistema de autenticação para a aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    # Configurar sessão
    app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(minutes=30)
    
    # Verificar expiração de sessão
    @app.before_request
    def verificar_sessao():
        if "usuario_id" in session and "ultimo_acesso" in session:
            # Carregar configuração
            sistema_usuarios = SistemaUsuarios()
            with open(sistema_usuarios.arquivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            tempo_expiracao = config["sessao"]["tempo_expiracao_minutos"]
            
            # Verificar tempo desde o último acesso
            ultimo_acesso = datetime.datetime.fromisoformat(session["ultimo_acesso"])
            agora = datetime.datetime.now()
            
            if (agora - ultimo_acesso).total_seconds() > (tempo_expiracao * 60):
                # Sessão expirada
                session.clear()
                flash("Sua sessão expirou. Por favor, faça login novamente.", "warning")
                return redirect(url_for("login"))
            
            # Atualizar último acesso
            session["ultimo_acesso"] = agora.isoformat()

# Adicionar rotas para o sistema de usuários
def adicionar_rotas_usuarios(app):
    """
    Adiciona rotas para o sistema de usuários à aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    from flask import request, jsonify, render_template, redirect, url_for, flash
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            login = request.form.get('login')
            senha = request.form.get('senha')
            
            if not login or not senha:
                flash("Por favor, preencha todos os campos.", "danger")
                return render_template('login.html')
            
            sistema_usuarios = SistemaUsuarios()
            resultado = sistema_usuarios.autenticar_usuario(login, senha, request.remote_addr)
            
            if resultado["sucesso"]:
                # Criar sessão
                session["usuario_id"] = resultado["usuario"]["id"]
                session["usuario_nome"] = resultado["usuario"]["nome"]
                session["usuario_login"] = resultado["usuario"]["login"]
                session["usuario_perfil"] = resultado["usuario"]["perfil"]
                session["usuario_permissoes"] = resultado["usuario"]["permissoes"]
                session["ultimo_acesso"] = datetime.datetime.now().isoformat()
                
                # Verificar se a senha está expirada
                if resultado["usuario"]["senha_expirada"]:
                    flash("Sua senha expirou. Por favor, altere-a agora.", "warning")
                    return redirect(url_for("alterar_senha"))
                
                # Redirecionar para a página solicitada ou para a página inicial
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))
            else:
                flash(resultado["mensagem"], "danger")
                return render_template('login.html')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        # Registrar logout
        if "usuario_id" in session:
            sistema_usuarios = SistemaUsuarios()
            conn = sqlite3.connect(sistema_usuarios.arquivo_db)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO logs_acesso (usuario_id, data, ip, acao, detalhes)
            VALUES (?, ?, ?, ?, ?)
            ''', (session["usuario_id"], 
                 datetime.datetime.now().isoformat(), 
                 request.remote_addr,
                 "logout", 
                 json.dumps({
                     "login": session.get("usuario_login")
                 })))
            
            conn.commit()
            conn.close()
        
        # Limpar sessão
        session.clear()
        
        flash("Você saiu do sistema.", "success")
        return redirect(url_for('login'))
    
    @app.route('/alterar_senha', methods=['GET', 'POST'])
    @requer_login
    def alterar_senha():
        if request.method == 'POST':
            senha_atual = request.form.get('senha_atual')
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            if not senha_atual or not nova_senha or not confirmar_senha:
                flash("Por favor, preencha todos os campos.", "danger")
                return render_template('alterar_senha.html')
            
            if nova_senha != confirmar_senha:
                flash("A nova senha e a confirmação não coincidem.", "danger")
                return render_template('alterar_senha.html')
            
            sistema_usuarios = SistemaUsuarios()
            resultado = sistema_usuarios.alterar_senha(session["usuario_id"], senha_atual, nova_senha)
            
            if resultado["sucesso"]:
                flash("Senha alterada com sucesso.", "success")
                return redirect(url_for('index'))
            else:
                flash(resultado["mensagem"], "danger")
                return render_template('alterar_senha.html')
        
        return render_template('alterar_senha.html')
    
    @app.route('/manutencao/usuarios')
    @requer_login
    @requer_permissao("usuarios.listar")
    def listar_usuarios():
        sistema_usuarios = SistemaUsuarios()
        usuarios = sistema_usuarios.listar_usuarios()
        
        return render_template('usuarios/listar.html', usuarios=usuarios)
    
    @app.route('/manutencao/usuarios/novo', methods=['GET', 'POST'])
    @requer_login
    @requer_permissao("usuarios.criar")
    def novo_usuario():
        if request.method == 'POST':
            nome = request.form.get('nome')
            login = request.form.get('login')
            email = request.form.get('email')
            perfil = request.form.get('perfil')
            senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            if not nome or not login or not perfil or not senha or not confirmar_senha:
                flash("Por favor, preencha todos os campos obrigatórios.", "danger")
                return render_template('usuarios/novo.html')
            
            if senha != confirmar_senha:
                flash("A senha e a confirmação não coincidem.", "danger")
                return render_template('usuarios/novo.html')
            
            sistema_usuarios = SistemaUsuarios()
            resultado = sistema_usuarios.criar_usuario(nome, login, senha, email, perfil)
            
            if resultado["sucesso"]:
                flash("Usuário criado com sucesso.", "success")
                return redirect(url_for('listar_usuarios'))
            else:
                flash(resultado["mensagem"], "danger")
                return render_template('usuarios/novo.html')
        
        # Carregar perfis disponíveis
        sistema_usuarios = SistemaUsuarios()
        with open(sistema_usuarios.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        perfis = config["perfis"]
        
        return render_template('usuarios/novo.html', perfis=perfis)
    
    @app.route('/manutencao/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
    @requer_login
    @requer_permissao("usuarios.editar")
    def editar_usuario(usuario_id):
        sistema_usuarios = SistemaUsuarios()
        
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            perfil = request.form.get('perfil')
            ativo = request.form.get('ativo') == 'on'
            
            if not nome or not perfil:
                flash("Por favor, preencha todos os campos obrigatórios.", "danger")
                usuario = sistema_usuarios.obter_usuario(usuario_id)
                return render_template('usuarios/editar.html', usuario=usuario)
            
            dados = {
                "nome": nome,
                "email": email,
                "perfil": perfil,
                "ativo": 1 if ativo else 0
            }
            
            resultado = sistema_usuarios.atualizar_usuario(usuario_id, dados)
            
            if resultado["sucesso"]:
                flash("Usuário atualizado com sucesso.", "success")
                return redirect(url_for('listar_usuarios'))
            else:
                flash(resultado["mensagem"], "danger")
                usuario = sistema_usuarios.obter_usuario(usuario_id)
                return render_template('usuarios/editar.html', usuario=usuario)
        
        usuario = sistema_usuarios.obter_usuario(usuario_id)
        
        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('listar_usuarios'))
        
        # Carregar perfis disponíveis
        with open(sistema_usuarios.arquivo_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        perfis = config["perfis"]
        
        return render_template('usuarios/editar.html', usuario=usuario, perfis=perfis)
    
    @app.route('/manutencao/usuarios/excluir/<int:usuario_id>', methods=['POST'])
    @requer_login
    @requer_permissao("usuarios.excluir")
    def excluir_usuario(usuario_id):
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.excluir_usuario(usuario_id)
        
        if resultado["sucesso"]:
            flash("Usuário excluído com sucesso.", "success")
        else:
            flash(resultado["mensagem"], "danger")
        
        return redirect(url_for('listar_usuarios'))
    
    @app.route('/manutencao/usuarios/redefinir_senha/<int:usuario_id>', methods=['POST'])
    @requer_login
    @requer_permissao("usuarios.redefinir_senha")
    def redefinir_senha_usuario(usuario_id):
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.redefinir_senha(usuario_id)
        
        if resultado["sucesso"]:
            flash(f"Senha redefinida com sucesso. Nova senha: {resultado['nova_senha']}", "success")
        else:
            flash(resultado["mensagem"], "danger")
        
        return redirect(url_for('listar_usuarios'))
    
    @app.route('/manutencao/usuarios/logs')
    @requer_login
    @requer_permissao("usuarios.logs")
    def logs_acesso():
        sistema_usuarios = SistemaUsuarios()
        
        # Parâmetros de filtro
        usuario_id = request.args.get('usuario_id')
        acao = request.args.get('acao')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        filtros = {}
        if usuario_id:
            filtros["usuario_id"] = usuario_id
        if acao:
            filtros["acao"] = acao
        if data_inicio:
            filtros["data_inicio"] = data_inicio
        if data_fim:
            filtros["data_fim"] = data_fim
        
        logs = sistema_usuarios.obter_logs_acesso(filtros)
        
        return render_template('usuarios/logs.html', logs=logs)
    
    # API para gerenciamento de usuários
    @app.route('/api/usuarios', methods=['GET'])
    @requer_login
    @requer_permissao("usuarios.listar")
    def api_listar_usuarios():
        sistema_usuarios = SistemaUsuarios()
        usuarios = sistema_usuarios.listar_usuarios()
        
        return jsonify(usuarios)
    
    @app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
    @requer_login
    @requer_permissao("usuarios.ler")
    def api_obter_usuario(usuario_id):
        sistema_usuarios = SistemaUsuarios()
        usuario = sistema_usuarios.obter_usuario(usuario_id)
        
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        return jsonify(usuario)
    
    @app.route('/api/usuarios', methods=['POST'])
    @requer_login
    @requer_permissao("usuarios.criar")
    def api_criar_usuario():
        dados = request.json
        
        if not dados or not all(k in dados for k in ["nome", "login", "senha", "perfil"]):
            return jsonify({"erro": "Dados incompletos"}), 400
        
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.criar_usuario(
            dados["nome"], 
            dados["login"], 
            dados["senha"], 
            dados.get("email"), 
            dados["perfil"]
        )
        
        if resultado["sucesso"]:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
    
    @app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
    @requer_login
    @requer_permissao("usuarios.editar")
    def api_atualizar_usuario(usuario_id):
        dados = request.json
        
        if not dados:
            return jsonify({"erro": "Dados vazios"}), 400
        
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.atualizar_usuario(usuario_id, dados)
        
        if resultado["sucesso"]:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
    
    @app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
    @requer_login
    @requer_permissao("usuarios.excluir")
    def api_excluir_usuario(usuario_id):
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.excluir_usuario(usuario_id)
        
        if resultado["sucesso"]:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
    
    @app.route('/api/usuarios/<int:usuario_id>/redefinir_senha', methods=['POST'])
    @requer_login
    @requer_permissao("usuarios.redefinir_senha")
    def api_redefinir_senha(usuario_id):
        dados = request.json
        nova_senha = dados.get("nova_senha") if dados else None
        
        sistema_usuarios = SistemaUsuarios()
        resultado = sistema_usuarios.redefinir_senha(usuario_id, nova_senha)
        
        if resultado["sucesso"]:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
