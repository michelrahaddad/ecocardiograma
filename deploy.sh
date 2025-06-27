#!/bin/bash

# Script de Deploy Automático para Render
# Sistema de Ecocardiograma - Grupo Vidah

echo "🚀 PREPARANDO DEPLOY PARA RENDER"
echo "================================="

# Verificar se estamos em um repositório git
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
fi

# Adicionar todos os arquivos
echo "📦 Adicionando arquivos ao Git..."
git add .

# Verificar se há mudanças para commit
if git diff --staged --quiet; then
    echo "ℹ️  Nenhuma mudança detectada para commit"
else
    # Fazer commit
    echo "💾 Fazendo commit das mudanças..."
    git commit -m "Deploy: Sistema Ecocardiograma Grupo Vidah - $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Executar verificação de prontidão
echo "🔍 Verificando prontidão para deploy..."
python prepare_deploy.py

# Verificar se o script de verificação passou
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SISTEMA PRONTO PARA DEPLOY!"
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo "1. Fazer push para o repositório remoto:"
    echo "   git remote add origin https://github.com/SEU_USUARIO/ecocardiograma-vidah.git"
    echo "   git push -u origin main"
    echo ""
    echo "2. No Render (render.com):"
    echo "   - Criar novo Web Service"
    echo "   - Conectar repositório"
    echo "   - Build Command: pip install -r deploy_requirements.txt"
    echo "   - Start Command: gunicorn --bind 0.0.0.0:\$PORT --workers 2 --timeout 120 --preload main:app"
    echo ""
    echo "3. Criar PostgreSQL Database:"
    echo "   - Nome: ecocardiograma-vidah-db"
    echo "   - Conectar DATABASE_URL automaticamente"
    echo ""
    echo "4. Configurar variáveis de ambiente:"
    echo "   - SESSION_SECRET (gerar automaticamente)"
    echo "   - FLASK_ENV=production"
    echo "   - FLASK_DEBUG=False"
    echo ""
    echo "📖 Consulte DEPLOY_RENDER.md para instruções detalhadas"
else
    echo ""
    echo "❌ SISTEMA PRECISA DE AJUSTES ANTES DO DEPLOY"
    echo "📖 Consulte o relatório gerado para mais detalhes"
fi

echo ""
echo "🎯 Deploy preparado! Boa sorte! 🚀"