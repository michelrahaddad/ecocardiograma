"""
Testes para Sistema de Autenticação
Garante funcionalidade crítica durante refatoração
"""

import unittest
import tempfile
import os
from app import app, db
from auth.models import AuthUser


class TestAuthentication(unittest.TestCase):
    """Testes do sistema de autenticação"""

    def setUp(self):
        """Configurar ambiente de teste"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Criar usuário de teste
            self.test_user = AuthUser(
                username='test_user',
                email='test@vidah.com',
                role='user',
                is_verified=True,
                is_active_flag=True
            )
            self.test_user.set_password('test123')
            db.session.add(self.test_user)
            
            # Criar admin de teste
            self.test_admin = AuthUser(
                username='test_admin',
                email='admin@vidah.com',
                role='admin',
                is_verified=True,
                is_active_flag=True
            )
            self.test_admin.set_password('admin123')
            db.session.add(self.test_admin)
            
            db.session.commit()

    def tearDown(self):
        """Limpar ambiente de teste"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_user_creation(self):
        """Teste criação de usuário"""
        with app.app_context():
            user = AuthUser.query.filter_by(username='test_user').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@vidah.com')
            self.assertTrue(user.check_password('test123'))

    def test_login_valid_user(self):
        """Teste login com usuário válido"""
        response = self.app.post('/login', data={
            'username': 'test_user',
            'password': 'test123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_password(self):
        """Teste login com senha inválida"""
        response = self.app.post('/login', data={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertIn(b'incorretos', response.data)

    def test_admin_access(self):
        """Teste acesso administrativo"""
        with app.app_context():
            admin = AuthUser.query.filter_by(username='test_admin').first()
            self.assertTrue(admin.is_admin())

    def test_user_is_active(self):
        """Teste verificação de usuário ativo"""
        with app.app_context():
            user = AuthUser.query.filter_by(username='test_user').first()
            self.assertTrue(user.is_active())


if __name__ == '__main__':
    unittest.main()