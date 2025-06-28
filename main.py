"""
Sistema de Ecocardiograma - Grupo Vidah
Entrada principal para deploy no Render - VERSÃO FINAL CORRIGIDA
Este arquivo deve substituir o main.py no GitHub
"""

from app_github_final import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
