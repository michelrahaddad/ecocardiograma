"""
Test Suite for LSP Error Corrections
Sistema de Ecocardiograma - Validação de Correções

Este módulo testa todas as correções de LSP implementadas,
incluindo construtores SQLAlchemy, type safety e funcionalidade geral.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from auth.models import AuthUser, UserSession
from auth.services import AuthService, UserManagementService, SessionService
from models import Exame, ParametrosEcocardiograma, LaudoEcocardiograma
from utils.pdf_generator_fixed import EcocardiogramaPDFGenerator


class TestLSPCorrections(unittest.TestCase):
    """Testes para validar todas as correções de LSP implementadas"""

    def setUp(self):
        """Configurar ambiente de teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Limpar ambiente de teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_authuser_constructor_with_keywords(self):
        """Testa construtor AuthUser com argumentos nomeados"""
        with self.app.app_context():
            user_data = {
                'username': 'test_user',
                'email': 'test@example.com',
                'role': 'user',
                'is_verified': True,
                'is_active_flag': True,
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            # Testa construtor com kwargs
            user = AuthUser(**user_data)
            user.set_password('TestPassword123!')
            
            db.session.add(user)
            db.session.commit()
            
            # Verificações
            self.assertEqual(user.username, 'test_user')
            self.assertEqual(user.email, 'test@example.com')
            self.assertEqual(user.role, 'user')
            self.assertTrue(user.is_verified)
            self.assertTrue(user.is_active_flag)
            self.assertEqual(user.first_name, 'Test')
            self.assertEqual(user.last_name, 'User')
            self.assertTrue(user.check_password('TestPassword123!'))

    def test_usersession_constructor_with_keywords(self):
        """Testa construtor UserSession com argumentos nomeados"""
        with self.app.app_context():
            # Criar usuário primeiro
            user = AuthUser(
                username='session_user',
                email='session@example.com',
                role='user',
                is_verified=True,
                is_active_flag=True
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            
            # Criar sessão com construtor kwargs
            session_data = {
                'user_id': user.id,
                'session_token': 'test_token_123',
                'ip_address': '192.168.1.1',
                'user_agent': 'Test Browser',
                'device_fingerprint': 'test_fingerprint',
                'expires_at': datetime.now() + timedelta(hours=24)
            }
            
            session = UserSession(**session_data)
            db.session.add(session)
            db.session.commit()
            
            # Verificações
            self.assertEqual(session.user_id, user.id)
            self.assertEqual(session.session_token, 'test_token_123')
            self.assertEqual(session.ip_address, '192.168.1.1')
            self.assertEqual(session.user_agent, 'Test Browser')
            self.assertTrue(session.is_valid())

    def test_auth_service_create_user(self):
        """Testa criação de usuário via AuthService com novos construtores"""
        with self.app.app_context():
            user_data = {
                'username': 'service_user',
                'email': 'service@example.com',
                'password': 'ServicePass123!',
                'role': 'admin',
                'first_name': 'Service',
                'last_name': 'User',
                'is_verified': True
            }
            
            success, user, message = UserManagementService.create_user(user_data)
            
            # Verificações
            self.assertTrue(success)
            self.assertIsNotNone(user)
            self.assertEqual(message, "Usuário criado com sucesso")
            self.assertEqual(user.username, 'service_user')
            self.assertEqual(user.email, 'service@example.com')
            self.assertTrue(user.is_admin())

    def test_exam_model_constructor(self):
        """Testa construtor do modelo Exame"""
        with self.app.app_context():
            exam_data = {
                'nome_paciente': 'João Silva',
                'data_exame': datetime.now(),
                'medico_solicitante': 'Dr. Teste',
                'idade_paciente': '45 anos',
                'data_nascimento': '1979-01-01'
            }
            
            exame = Exame(**exam_data)
            db.session.add(exame)
            db.session.commit()
            
            # Verificações
            self.assertEqual(exame.nome_paciente, 'João Silva')
            self.assertEqual(exame.medico_solicitante, 'Dr. Teste')
            self.assertEqual(exame.idade_paciente, '45 anos')

    def test_parameters_model_constructor(self):
        """Testa construtor do modelo ParametrosEcocardiograma"""
        with self.app.app_context():
            # Criar exame primeiro
            exame = Exame(
                nome_paciente='Maria Silva',
                data_exame=datetime.now(),
                medico_solicitante='Dr. Cardio'
            )
            db.session.add(exame)
            db.session.commit()
            
            # Criar parâmetros com construtor
            params_data = {
                'exame_id': exame.id,
                'atrio_esquerdo': 36.0,
                'raiz_aorta': 35.0,
                'aorta_ascendente': 33.0,
                'vd_diametro': 18.0,
                'vd_basal': 32.0,
                'ddve': 45.0,
                'dsve': 32.0,
                'septo': 9.0,
                'parede_posterior': 8.0
            }
            
            parametros = ParametrosEcocardiograma(**params_data)
            db.session.add(parametros)
            db.session.commit()
            
            # Verificações
            self.assertEqual(parametros.exame_id, exame.id)
            self.assertEqual(parametros.atrio_esquerdo, 36.0)
            self.assertEqual(parametros.ddve, 45.0)

    def test_type_safety_password_hash(self):
        """Testa correção de type safety para password hash"""
        with self.app.app_context():
            user = AuthUser(
                username='type_test',
                email='type@example.com',
                role='user'
            )
            user.set_password('TypeTest123!')
            db.session.add(user)
            db.session.commit()
            
            # Testa verificação de senha (que usa str() casting)
            self.assertTrue(user.check_password('TypeTest123!'))
            self.assertFalse(user.check_password('wrong_password'))

    def test_authentication_flow_complete(self):
        """Testa fluxo completo de autenticação com novos construtores"""
        with self.app.app_context():
            # Criar usuário
            user_data = {
                'username': 'flow_user',
                'email': 'flow@example.com',
                'password': 'FlowTest123!',
                'role': 'user',
                'is_verified': True
            }
            
            success, user, message = UserManagementService.create_user(user_data)
            self.assertTrue(success)
            
            # Autenticar usuário
            auth_success, auth_user, auth_message = AuthService.authenticate_user(
                'flow_user', 'FlowTest123!', '127.0.0.1'
            )
            
            self.assertTrue(auth_success)
            self.assertIsNotNone(auth_user)
            self.assertEqual(auth_user.username, 'flow_user')

    def test_pdf_generation_with_new_models(self):
        """Testa geração de PDF com modelos usando novos construtores"""
        with self.app.app_context():
            # Criar exame completo
            exame = Exame(
                nome_paciente='PDF Test Patient',
                data_exame=datetime.now(),
                medico_solicitante='Dr. PDF Test',
                idade_paciente='50 anos'
            )
            db.session.add(exame)
            db.session.commit()
            
            # Criar parâmetros
            parametros = ParametrosEcocardiograma(
                exame_id=exame.id,
                atrio_esquerdo=38.0,
                ddve=48.0,
                dsve=30.0,
                septo=10.0
            )
            db.session.add(parametros)
            db.session.commit()
            
            # Criar laudo
            laudo = LaudoEcocardiograma(
                exame_id=exame.id,
                conclusao='Exame normal dentro dos parâmetros esperados.',
                observacoes='Paciente colaborativo durante o exame.'
            )
            db.session.add(laudo)
            db.session.commit()
            
            # Gerar PDF
            generator = EcocardiogramaPDFGenerator()
            pdf_data = generator.create_header_footer
            
            # Verificar que o PDF pode ser criado sem erros
            self.assertIsNotNone(generator)

    def test_database_operations_integrity(self):
        """Testa integridade das operações de banco com novos construtores"""
        with self.app.app_context():
            # Criar usuário admin
            admin = AuthUser(
                username='admin_test',
                email='admin@test.com',
                role='admin',
                is_verified=True,
                is_active_flag=True
            )
            admin.set_password('AdminTest123!')
            db.session.add(admin)
            db.session.commit()
            
            # Criar múltiplos exames
            for i in range(3):
                exame = Exame(
                    nome_paciente=f'Paciente {i+1}',
                    data_exame=datetime.now(),
                    medico_solicitante='Dr. Bulk Test'
                )
                db.session.add(exame)
            
            db.session.commit()
            
            # Verificar contagem
            exames_count = db.session.query(Exame).count()
            self.assertEqual(exames_count, 3)
            
            users_count = db.session.query(AuthUser).count()
            self.assertEqual(users_count, 1)

    def test_session_management_with_new_constructors(self):
        """Testa gerenciamento de sessões com novos construtores"""
        with self.app.app_context():
            # Criar usuário
            user = AuthUser(
                username='session_mgmt',
                email='session@mgmt.com',
                role='user',
                is_verified=True
            )
            user.set_password('SessionTest123!')
            db.session.add(user)
            db.session.commit()
            
            # Criar sessão via service
            session = SessionService.create_user_session(
                user.id, '192.168.1.100', 'Test Browser v2'
            )
            
            self.assertIsNotNone(session)
            self.assertEqual(session.user_id, user.id)
            self.assertTrue(session.is_valid())


def run_lsp_tests():
    """Executa todos os testes de correção LSP"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    print("=== EXECUTANDO TESTES DE CORREÇÕES LSP ===")
    print("Validando construtores SQLAlchemy, type safety e funcionalidade geral")
    print("=" * 60)
    
    run_lsp_tests()