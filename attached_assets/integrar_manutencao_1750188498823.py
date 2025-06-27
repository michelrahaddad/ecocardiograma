"""
Script para integrar as funções de manutenção ao sistema principal.

Este script deve ser executado para adicionar as funções de manutenção ao arquivo main.py.
"""

import os
import sys
import re

def integrar_manutencao():
    """Integra as funções de manutenção ao sistema principal."""
    
    # Caminho para o arquivo main.py
    main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    
    if not os.path.exists(main_path):
        print(f"Erro: Arquivo main.py não encontrado em {main_path}")
        return False
    
    # Ler o conteúdo do arquivo main.py
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se a integração já foi feita
    if "from manutencao import configurar_manutencao" in content:
        print("As funções de manutenção já estão integradas ao sistema principal.")
        return True
    
    # Adicionar importação
    import_pattern = r"(from flask import .*)"
    import_replacement = r"\1\n\n# Importar módulo de manutenção\nfrom manutencao import configurar_manutencao"
    
    content = re.sub(import_pattern, import_replacement, content)
    
    # Adicionar configuração
    app_pattern = r"(app = Flask\(__name__\))"
    app_replacement = r"\1\n\n# Configurar funções de manutenção\nconfiguracao_manutencao = True  # Definir como False para desativar\n\nif configuracao_manutencao:\n    try:\n        configurar_manutencao(app)\n        print('Funções de manutenção configuradas com sucesso')\n    except Exception as e:\n        print(f'Erro ao configurar funções de manutenção: {str(e)}')"
    
    content = re.sub(app_pattern, app_replacement, content)
    
    # Adicionar rota para o painel de manutenção
    route_pattern = r"(if __name__ == '__main__':)"
    route_replacement = r"# Rota para o painel de manutenção\n@app.route('/manutencao/executar_testes', methods=['POST'])\ndef executar_testes_manutencao():\n    from manutencao.testes import executar_testes\n    resultado = executar_testes()\n    return jsonify(resultado)\n\n\1"
    
    content = re.sub(route_pattern, route_replacement, content)
    
    # Salvar as alterações
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Funções de manutenção integradas com sucesso ao sistema principal.")
    return True

if __name__ == "__main__":
    integrar_manutencao()
