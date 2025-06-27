#!/usr/bin/env python3
"""
Script para criar usuário de teste no sistema
"""

import sys
import os
sys.path.append('.')

from app import app, db
from auth.models import AuthUser
from models import datetime_brasilia

def create_test_user():
    """Cria usuário comum para testes"""
    with app.app_context():
        # Verificar se usuário já existe
        existing_user = AuthUser.query.filter_by(username='usuario').first()
        if existing_user:
            print("Usuário 'usuario' já existe")
            return
        
        # Criar usuário comum
        user = AuthUser(
            username='usuario',
            email='usuario@vidah.com',
            role='user',
            first_name='João',
            last_name='Silva',
            is_verified=True,
            is_active_flag=True
        )
        
        # Definir senha
        user.set_password('Usuario123!')
        
        # Salvar no banco
        db.session.add(user)
        db.session.commit()
        
        print("✅ Usuário criado com sucesso!")
        print("📝 Login: usuario")
        print("🔑 Senha: Usuario123!")
        print("👤 Tipo: Usuário comum")

if __name__ == '__main__':
    create_test_user()