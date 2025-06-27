"""
Módulo de Testes de Manutenção

Este módulo implementa testes para validar as funções de manutenção.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
import sqlite3
import datetime
import logging

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('testes_manutencao')

class TestesManutencao(unittest.TestCase):
    """Classe de testes para as funções de manutenção."""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes."""
        # Diretório base do projeto
        cls.diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Diretório temporário para testes
        cls.diretorio_temp = tempfile.mkdtemp()
        
        # Criar estrutura de diretórios para testes
        os.makedirs(os.path.join(cls.diretorio_temp, "config"), exist_ok=True)
        os.makedirs(os.path.join(cls.diretorio_temp, "logs"), exist_ok=True)
        os.makedirs(os.path.join(cls.diretorio_temp, "backups"), exist_ok=True)
        os.makedirs(os.path.join(cls.diretorio_temp, "diagnostico"), exist_ok=True)
        os.makedirs(os.path.join(cls.diretorio_temp, "integridade"), exist_ok=True)
        
        # Criar banco de dados de teste
        cls.criar_banco_dados_teste()
        
        logger.info(f"Configuração de testes concluída. Diretório temporário: {cls.diretorio_temp}")
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após todos os testes."""
        # Remover diretório temporário
        shutil.rmtree(cls.diretorio_temp)
        
        logger.info("Limpeza de testes concluída")
    
    @classmethod
    def criar_banco_dados_teste(cls):
        """Cria um banco de dados SQLite de teste."""
        db_path = os.path.join(cls.diretorio_temp, "ecocardiograma.db")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabelas de teste
        cursor.execute('''
        CREATE TABLE exames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_nome TEXT NOT NULL,
            data TEXT NOT NULL,
            medico_id INTEGER,
            status TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT NOT NULL,
            especialidade TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE laudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exame_id INTEGER,
            texto TEXT,
            data TEXT,
            FOREIGN KEY (exame_id) REFERENCES exames (id)
        )
        ''')
        
        # Inserir dados de teste
        cursor.execute("INSERT INTO medicos (nome, crm, especialidade) VALUES (?, ?, ?)",
                      ("Dr. Teste", "12345", "Cardiologia"))
        
        cursor.execute("INSERT INTO exames (paciente_nome, data, medico_id, status) VALUES (?, ?, ?, ?)",
                      ("Paciente Teste", datetime.datetime.now().isoformat(), 1, "concluído"))
        
        cursor.execute("INSERT INTO laudos (exame_id, texto, data) VALUES (?, ?, ?)",
                      (1, "Laudo de teste", datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Banco de dados de teste criado: {db_path}")
    
    def test_atualizacao(self):
        """Testa o módulo de atualização automática."""
        try:
            from manutencao.atualizacao import SistemaAtualizacao
            
            # Criar instância com diretório temporário
            sistema = SistemaAtualizacao()
            sistema.diretorio_base = self.diretorio_temp
            
            # Testar verificação de atualizações
            resultado = sistema.verificar_atualizacoes()
            
            # Verificar se o resultado é um dicionário
            self.assertIsInstance(resultado, dict)
            
            logger.info("Teste de atualização concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de atualização falhou: {str(e)}")
    
    def test_backup(self):
        """Testa o módulo de backup e restauração."""
        try:
            from manutencao.backup import SistemaBackup
            
            # Criar instância com diretório temporário
            sistema = SistemaBackup()
            sistema.diretorio_base = self.diretorio_temp
            sistema.diretorio_backup = os.path.join(self.diretorio_temp, "backups")
            
            # Testar criação de backup
            resultado = sistema.criar_backup("Backup de teste")
            
            # Verificar se o backup foi criado
            self.assertTrue(resultado)
            self.assertTrue(os.path.exists(resultado))
            
            # Testar listagem de backups
            backups = sistema.listar_backups()
            self.assertIsInstance(backups, list)
            self.assertEqual(len(backups), 1)
            
            logger.info("Teste de backup concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de backup falhou: {str(e)}")
    
    def test_logs(self):
        """Testa o módulo de sistema de logs."""
        try:
            from manutencao.logs import SistemaLogs
            
            # Criar instância com diretório temporário
            sistema = SistemaLogs()
            sistema.diretorio_base = self.diretorio_temp
            
            # Testar registro de log
            sistema.registrar_log("teste", "Mensagem de teste", {"detalhe": "valor"})
            
            # Testar busca de logs
            logs = sistema.buscar_logs()
            self.assertIsInstance(logs, list)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["categoria"], "teste")
            
            logger.info("Teste de logs concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de logs falhou: {str(e)}")
    
    def test_diagnostico(self):
        """Testa o módulo de diagnóstico e relatórios."""
        try:
            from manutencao.diagnostico import SistemaDiagnostico
            
            # Criar instância com diretório temporário
            sistema = SistemaDiagnostico()
            sistema.diretorio_base = self.diretorio_temp
            
            # Testar diagnóstico do sistema
            resultado = sistema.diagnosticar_sistema()
            
            # Verificar se o resultado é um dicionário
            self.assertIsInstance(resultado, dict)
            
            logger.info("Teste de diagnóstico concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de diagnóstico falhou: {str(e)}")
    
    def test_integridade(self):
        """Testa o módulo de verificação de integridade."""
        try:
            from manutencao.integridade import SistemaIntegridade
            
            # Criar instância com diretório temporário
            sistema = SistemaIntegridade()
            sistema.diretorio_base = self.diretorio_temp
            
            # Testar geração de assinaturas
            assinaturas = sistema.gerar_assinaturas()
            
            # Verificar se o resultado é um dicionário
            self.assertIsInstance(assinaturas, dict)
            
            # Testar verificação de integridade
            resultado = sistema.verificar_integridade()
            self.assertIsInstance(resultado, dict)
            
            logger.info("Teste de integridade concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de integridade falhou: {str(e)}")
    
    def test_limpeza(self):
        """Testa o módulo de limpeza de arquivos temporários."""
        try:
            from manutencao.limpeza import SistemaLimpeza
            
            # Criar instância com diretório temporário
            sistema = SistemaLimpeza()
            sistema.diretorio_base = self.diretorio_temp
            
            # Criar alguns arquivos temporários para teste
            os.makedirs(os.path.join(self.diretorio_temp, "temp"), exist_ok=True)
            with open(os.path.join(self.diretorio_temp, "temp", "teste.tmp"), "w") as f:
                f.write("Arquivo temporário de teste")
            
            # Testar identificação de arquivos temporários
            resultado = sistema.identificar_arquivos_temporarios()
            
            # Verificar se o resultado é um dicionário
            self.assertIsInstance(resultado, dict)
            
            logger.info("Teste de limpeza concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de limpeza falhou: {str(e)}")
    
    def test_usuarios(self):
        """Testa o módulo de gerenciamento de usuários."""
        try:
            from manutencao.usuarios import SistemaUsuarios
            
            # Criar instância com diretório temporário
            sistema = SistemaUsuarios()
            sistema.diretorio_base = self.diretorio_temp
            sistema.arquivo_db = os.path.join(self.diretorio_temp, "ecocardiograma.db")
            
            # Testar criação de usuário
            resultado = sistema.criar_usuario(
                "Usuário Teste",
                "teste",
                "Senha@123",
                "teste@exemplo.com",
                "medico"
            )
            
            # Verificar se o usuário foi criado
            self.assertTrue(resultado["sucesso"])
            
            # Testar autenticação
            auth = sistema.autenticar_usuario("teste", "Senha@123")
            self.assertTrue(auth["sucesso"])
            
            # Testar listagem de usuários
            usuarios = sistema.listar_usuarios()
            self.assertIsInstance(usuarios, list)
            self.assertGreaterEqual(len(usuarios), 1)
            
            logger.info("Teste de usuários concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de usuários falhou: {str(e)}")
    
    def test_instalador(self):
        """Testa o módulo de instalador/desinstalador."""
        try:
            from manutencao.instalador import SistemaInstalador
            
            # Criar instância com diretório temporário
            sistema = SistemaInstalador()
            sistema.diretorio_base = self.diretorio_temp
            
            # Testar verificação de requisitos
            resultado = sistema.verificar_requisitos_sistema()
            
            # Verificar se o resultado é um dicionário
            self.assertIsInstance(resultado, dict)
            
            logger.info("Teste de instalador concluído com sucesso")
        except Exception as e:
            self.fail(f"Teste de instalador falhou: {str(e)}")
    
    def test_integracao(self):
        """Testa a integração de todos os módulos."""
        try:
            # Criar uma aplicação Flask de teste
            from flask import Flask
            app = Flask(__name__)
            
            # Importar módulo de integração
            from manutencao import configurar_manutencao
            
            # Configurar manutenção (sem executar)
            # Apenas verificar se não há erros de importação ou configuração
            try:
                # Não executar de fato, apenas verificar se as funções existem
                self.assertTrue(callable(configurar_manutencao))
                logger.info("Teste de integração concluído com sucesso")
            except Exception as e:
                self.fail(f"Teste de integração falhou: {str(e)}")
        except Exception as e:
            self.fail(f"Teste de integração falhou: {str(e)}")

def executar_testes():
    """Executa todos os testes de manutenção."""
    # Configurar suite de testes
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestesManutencao))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Retornar resultado
    return {
        "total": resultado.testsRun,
        "falhas": len(resultado.failures),
        "erros": len(resultado.errors),
        "sucesso": resultado.wasSuccessful()
    }

if __name__ == "__main__":
    # Executar testes quando o script é executado diretamente
    resultado = executar_testes()
    
    print("\n" + "="*50)
    print(f"Total de testes: {resultado['total']}")
    print(f"Falhas: {resultado['falhas']}")
    print(f"Erros: {resultado['erros']}")
    print(f"Sucesso: {'Sim' if resultado['sucesso'] else 'Não'}")
    print("="*50)
    
    # Sair com código de erro se houver falhas
    sys.exit(0 if resultado['sucesso'] else 1)
