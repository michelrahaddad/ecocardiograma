import os
import json
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from docx import Document
import re

class IntegradorModelosLaudo:
    def __init__(self, app, diretorio_modelos_txt, diretorio_modelos_docx):
        """
        Inicializa o integrador de modelos de laudo
        
        Args:
            app: Aplicação Flask
            diretorio_modelos_txt: Diretório com modelos em formato TXT
            diretorio_modelos_docx: Diretório com modelos em formato DOCX
        """
        self.app = app
        self.diretorio_modelos_txt = diretorio_modelos_txt
        self.diretorio_modelos_docx = diretorio_modelos_docx
        self.modelos_cache = None
        
        # Registrar rotas
        self.registrar_rotas()
        
    def registrar_rotas(self):
        """Registra as rotas necessárias para a funcionalidade"""
        
        @self.app.route('/buscar_modelos')
        def buscar_modelos():
            termo = request.args.get('termo', '').lower()
            if len(termo) < 2:
                return jsonify({'modelos': []})
                
            modelos = self.buscar_modelos_por_termo(termo)
            return jsonify({'modelos': modelos})
            
        @self.app.route('/obter_modelo/<modelo_id>')
        def obter_modelo(modelo_id):
            modelo = self.obter_modelo_por_id(modelo_id)
            if modelo:
                return jsonify({'modelo': modelo})
            return jsonify({'erro': 'Modelo não encontrado'}), 404
            
        @self.app.route('/listar_modelos')
        def listar_modelos():
            modelos = self.listar_todos_modelos()
            return render_template('modelos_disponiveis.html', modelos=modelos)
    
    def carregar_modelos(self):
        """Carrega todos os modelos disponíveis"""
        if self.modelos_cache is not None:
            return self.modelos_cache
            
        modelos = []
        
        # Carregar modelos TXT
        if os.path.exists(self.diretorio_modelos_txt):
            for arquivo in os.listdir(self.diretorio_modelos_txt):
                if arquivo.endswith('.txt'):
                    caminho_completo = os.path.join(self.diretorio_modelos_txt, arquivo)
                    nome_modelo = os.path.splitext(arquivo)[0]
                    
                    try:
                        with open(caminho_completo, 'r', encoding='utf-8') as f:
                            conteudo = f.read()
                            
                        # Extrair campos do conteúdo
                        campos = self.extrair_campos_txt(conteudo)
                        
                        modelos.append({
                            'id': f'txt_{nome_modelo}',
                            'nome': nome_modelo,
                            'tipo': 'Texto',
                            'formato': 'txt',
                            'caminho': caminho_completo,
                            **campos
                        })
                    except Exception as e:
                        print(f"Erro ao carregar modelo TXT {arquivo}: {e}")
        
        # Carregar modelos DOCX
        if os.path.exists(self.diretorio_modelos_docx):
            for arquivo in os.listdir(self.diretorio_modelos_docx):
                if arquivo.endswith('.docx'):
                    caminho_completo = os.path.join(self.diretorio_modelos_docx, arquivo)
                    nome_modelo = os.path.splitext(arquivo)[0]
                    
                    try:
                        # Extrair campos do documento DOCX
                        campos = self.extrair_campos_docx(caminho_completo)
                        
                        # Determinar tipo de paciente com base no nome do arquivo
                        tipo_paciente = 'Adulto'
                        if 'pediatrico' in arquivo.lower():
                            tipo_paciente = 'Pediátrico'
                        
                        modelos.append({
                            'id': f'docx_{nome_modelo}',
                            'nome': self.formatar_nome_modelo(nome_modelo),
                            'tipo': tipo_paciente,
                            'formato': 'docx',
                            'caminho': caminho_completo,
                            **campos
                        })
                    except Exception as e:
                        print(f"Erro ao carregar modelo DOCX {arquivo}: {e}")
        
        self.modelos_cache = modelos
        return modelos
    
    def formatar_nome_modelo(self, nome):
        """Formata o nome do modelo para exibição"""
        # Remover prefixos comuns
        nome = re.sub(r'^laudo_ecocardiograma_', '', nome)
        
        # Substituir underscores por espaços
        nome = nome.replace('_', ' ')
        
        # Capitalizar palavras
        nome = ' '.join(palavra.capitalize() for palavra in nome.split())
        
        return nome
    
    def extrair_campos_txt(self, conteudo):
        """Extrai campos de um modelo em formato TXT"""
        linhas = conteudo.split('\n')
        
        # Campos padrão
        campos = {
            'resumo_exame': '',
            'ritmo_cardiaco': '',
            'ventriculo_esquerdo': '',
            'ventriculo_direito': '',
            'valvas': '',
            'pericardio': '',
            'aorta': '',
            'conclusao': ''
        }
        
        # Tentar identificar seções no texto
        secao_atual = None
        conteudo_secao = []
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue
                
            # Verificar se é um cabeçalho de seção
            linha_lower = linha.lower()
            
            if 'resumo do exame' in linha_lower or 'resumo' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'resumo_exame'
                conteudo_secao = []
            elif 'ritmo' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'ritmo_cardiaco'
                conteudo_secao = []
            elif 'ventrículo esquerdo' in linha_lower or 've:' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'ventriculo_esquerdo'
                conteudo_secao = []
            elif 'ventrículo direito' in linha_lower or 'vd:' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'ventriculo_direito'
                conteudo_secao = []
            elif 'valvas' in linha_lower or 'valvular' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'valvas'
                conteudo_secao = []
            elif 'pericárdio' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'pericardio'
                conteudo_secao = []
            elif 'aorta' in linha_lower or 'grandes vasos' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'aorta'
                conteudo_secao = []
            elif 'conclusão' in linha_lower or 'conclusao' in linha_lower:
                if secao_atual and conteudo_secao:
                    campos[secao_atual] = '\n'.join(conteudo_secao)
                secao_atual = 'conclusao'
                conteudo_secao = []
            elif secao_atual:
                conteudo_secao.append(linha)
        
        # Adicionar a última seção
        if secao_atual and conteudo_secao:
            campos[secao_atual] = '\n'.join(conteudo_secao)
            
        # Se não conseguiu extrair campos específicos, usar todo o conteúdo como conclusão
        if all(not valor for valor in campos.values()):
            campos['conclusao'] = conteudo
            
        return campos
    
    def extrair_campos_docx(self, caminho_arquivo):
        """Extrai campos de um modelo em formato DOCX"""
        doc = Document(caminho_arquivo)
        texto_completo = '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        
        # Usar a mesma lógica do TXT para extrair campos
        return self.extrair_campos_txt(texto_completo)
    
    def buscar_modelos_por_termo(self, termo):
        """Busca modelos que correspondem ao termo informado"""
        modelos = self.carregar_modelos()
        resultados = []
        
        for modelo in modelos:
            # Buscar no nome do modelo
            if termo.lower() in modelo['nome'].lower():
                resultados.append(modelo)
                continue
                
            # Buscar no conteúdo dos campos
            for campo, valor in modelo.items():
                if campo not in ['id', 'nome', 'tipo', 'formato', 'caminho'] and isinstance(valor, str):
                    if termo.lower() in valor.lower():
                        resultados.append(modelo)
                        break
        
        return resultados
    
    def obter_modelo_por_id(self, modelo_id):
        """Obtém um modelo pelo ID"""
        modelos = self.carregar_modelos()
        
        for modelo in modelos:
            if modelo['id'] == modelo_id:
                return modelo
                
        return None
    
    def listar_todos_modelos(self):
        """Lista todos os modelos disponíveis"""
        modelos = self.carregar_modelos()
        
        # Agrupar por tipo
        modelos_agrupados = {
            'Adulto': [],
            'Pediátrico': []
        }
        
        for modelo in modelos:
            tipo = modelo['tipo']
            if tipo == 'Texto':
                # Determinar tipo com base no conteúdo
                if 'pediátrico' in modelo['nome'].lower():
                    tipo = 'Pediátrico'
                else:
                    tipo = 'Adulto'
            
            if tipo in modelos_agrupados:
                modelos_agrupados[tipo].append(modelo)
            else:
                modelos_agrupados['Adulto'].append(modelo)
        
        return modelos_agrupados

# Função para integrar ao aplicativo Flask existente
def integrar_modelos_laudo(app, diretorio_base):
    """
    Integra a funcionalidade de modelos de laudo ao aplicativo Flask
    
    Args:
        app: Aplicação Flask
        diretorio_base: Diretório base do sistema
    """
    diretorio_modelos_txt = os.path.join(diretorio_base, 'src', 'modelos_laudo')
    diretorio_modelos_docx = os.path.join(diretorio_base, 'modelos')
    
    # Criar diretório de modelos DOCX se não existir
    if not os.path.exists(diretorio_modelos_docx):
        os.makedirs(diretorio_modelos_docx)
    
    # Inicializar integrador
    integrador = IntegradorModelosLaudo(app, diretorio_modelos_txt, diretorio_modelos_docx)
    
    # Adicionar template para listagem de modelos
    criar_template_listagem_modelos(diretorio_base)
    
    return integrador

def criar_template_listagem_modelos(diretorio_base):
    """Cria o template para listagem de modelos"""
    diretorio_templates = os.path.join(diretorio_base, 'src', 'templates')
    caminho_template = os.path.join(diretorio_templates, 'modelos_disponiveis.html')
    
    conteudo_template = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modelos de Laudos Disponíveis - Sistema de Ecocardiograma</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        .modelos-container {
            margin: 20px 0;
        }
        
        .modelo-tipo {
            margin-bottom: 30px;
        }
        
        .modelo-tipo-titulo {
            font-size: 1.5rem;
            color: #0a2853;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #0a2853;
        }
        
        .modelos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .modelo-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .modelo-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .modelo-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .modelo-icon {
            font-size: 24px;
            margin-right: 10px;
            color: #41828e;
        }
        
        .modelo-titulo {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin: 0;
        }
        
        .modelo-formato {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-top: 5px;
        }
        
        .formato-txt {
            background-color: #e3f2fd;
            color: #1565c0;
        }
        
        .formato-docx {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        
        .modelo-acoes {
            margin-top: 15px;
            display: flex;
            justify-content: flex-end;
        }
        
        .modelo-btn {
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: background-color 0.2s;
        }
        
        .btn-aplicar {
            background-color: #0a2853;
            color: white;
        }
        
        .btn-aplicar:hover {
            background-color: #0d3268;
        }
        
        .btn-visualizar {
            background-color: #f8f9fa;
            color: #333;
            border: 1px solid #ddd;
            margin-right: 10px;
        }
        
        .btn-visualizar:hover {
            background-color: #e9ecef;
        }
        
        .voltar-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 15px;
            background-color: #f8f9fa;
            color: #333;
            border: 1px solid #ddd;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            margin-bottom: 20px;
            transition: background-color 0.2s;
        }
        
        .voltar-btn:hover {
            background-color: #e9ecef;
        }
        
        .empty-message {
            padding: 20px;
            text-align: center;
            color: #666;
            font-style: italic;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px dashed #ddd;
        }
    </style>
</head>
<body>
    <!-- Skip link para acessibilidade -->
    <a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>
    
    <!-- Cabeçalho -->
    <header class="eco-header">
        <div class="header-left">
            <img src="{{ url_for('static', filename='img/logo_vidah_site.png') }}" alt="Grupo Vidah" class="eco-logo">
        </div>
        <div class="header-center">
            <h1 class="eco-title">Sistema de Ecocardiograma</h1>
        </div>
        <div class="header-right">
            <button class="theme-toggle" id="theme-toggle" aria-label="Alternar tema claro/escuro">
                <i class="fas fa-moon"></i>
                <span>Modo escuro</span>
            </button>
            <div class="language-selector">
                <select id="language-select" aria-label="Selecionar idioma">
                    <option value="pt-br" selected>Português</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                </select>
            </div>
        </div>
    </header>
    
    <!-- Navegação principal -->
    <nav class="eco-nav">
        <ul class="eco-nav-list">
            <li class="eco-nav-item"><a href="{{ url_for('index') }}">Início</a></li>
            <li class="eco-nav-item"><a href="{{ url_for('novo_exame') }}">Novo Exame</a></li>
            <li class="eco-nav-item active"><a href="{{ url_for('listar_modelos') }}">Modelos de Laudos</a></li>
        </ul>
    </nav>
    
    <!-- Conteúdo principal -->
    <main id="main-content" class="container">
        <div class="eco-section">
            <div class="eco-section-header">
                <h2 class="eco-section-title">Modelos de Laudos Disponíveis</h2>
            </div>
            
            <a href="{{ url_for('index') }}" class="voltar-btn">
                <i class="fas fa-arrow-left"></i> Voltar à Página Inicial
            </a>
            
            <div class="modelos-container">
                <!-- Modelos para Adultos -->
                <div class="modelo-tipo">
                    <h3 class="modelo-tipo-titulo">Modelos para Adultos</h3>
                    
                    {% if modelos['Adulto'] %}
                    <div class="modelos-grid">
                        {% for modelo in modelos['Adulto'] %}
                        <div class="modelo-card">
                            <div class="modelo-header">
                                <div class="modelo-icon">
                                    {% if modelo.formato == 'docx' %}
                                    <i class="fas fa-file-word"></i>
                                    {% else %}
                                    <i class="fas fa-file-alt"></i>
                                    {% endif %}
                                </div>
                                <h4 class="modelo-titulo">{{ modelo.nome }}</h4>
                            </div>
                            
                            <div>
                                <span class="modelo-formato {% if modelo.formato == 'docx' %}formato-docx{% else %}formato-txt{% endif %}">
                                    {{ modelo.formato.upper() }}
                                </span>
                            </div>
                            
                            <div class="modelo-acoes">
                                <button class="modelo-btn btn-visualizar" onclick="visualizarModelo('{{ modelo.id }}')">
                                    <i class="fas fa-eye"></i> Visualizar
                                </button>
                                <button class="modelo-btn btn-aplicar" onclick="aplicarModelo('{{ modelo.id }}')">
                                    <i class="fas fa-check"></i> Aplicar
                                </button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-message">
                        Nenhum modelo para adultos disponível.
                    </div>
                    {% endif %}
                </div>
                
                <!-- Modelos Pediátricos -->
                <div class="modelo-tipo">
                    <h3 class="modelo-tipo-titulo">Modelos Pediátricos</h3>
                    
                    {% if modelos['Pediátrico'] %}
                    <div class="modelos-grid">
                        {% for modelo in modelos['Pediátrico'] %}
                        <div class="modelo-card">
                            <div class="modelo-header">
                                <div class="modelo-icon">
                                    {% if modelo.formato == 'docx' %}
                                    <i class="fas fa-file-word"></i>
                                    {% else %}
                                    <i class="fas fa-file-alt"></i>
                                    {% endif %}
                                </div>
                                <h4 class="modelo-titulo">{{ modelo.nome }}</h4>
                            </div>
                            
                            <div>
                                <span class="modelo-formato {% if modelo.formato == 'docx' %}formato-docx{% else %}formato-txt{% endif %}">
                                    {{ modelo.formato.upper() }}
                                </span>
                            </div>
                            
                            <div class="modelo-acoes">
                                <button class="modelo-btn btn-visualizar" onclick="visualizarModelo('{{ modelo.id }}')">
                                    <i class="fas fa-eye"></i> Visualizar
                                </button>
                                <button class="modelo-btn btn-aplicar" onclick="aplicarModelo('{{ modelo.id }}')">
                                    <i class="fas fa-check"></i> Aplicar
                                </button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <div class="empty-message">
                        Nenhum modelo pediátrico disponível.
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </main>
    
    <!-- Rodapé -->
    <footer class="eco-footer">
        <div class="footer-content">
            <p>&copy; 2025 Sistema de Ecocardiograma - Grupo Vidah. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <!-- Scripts -->
    <script>
        // Função para visualizar um modelo
        function visualizarModelo(modeloId) {
            window.open(`/visualizar_modelo/${modeloId}`, '_blank');
        }
        
        // Função para aplicar um modelo
        function aplicarModelo(modeloId) {
            // Redirecionar para a página de laudo com o modelo selecionado
            const exameId = new URLSearchParams(window.location.search).get('exame_id');
            if (exameId) {
                window.location.href = `/laudo/${exameId}?modelo_id=${modeloId}`;
            } else {
                alert('É necessário selecionar um exame antes de aplicar um modelo.');
                window.location.href = '/';
            }
        }
        
        // Alternar tema claro/escuro
        document.getElementById('theme-toggle').addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            const icon = this.querySelector('i');
            const text = this.querySelector('span');
            
            if (document.body.classList.contains('dark-theme')) {
                icon.className = 'fas fa-sun';
                text.textContent = 'Modo claro';
                localStorage.setItem('theme', 'dark');
            } else {
                icon.className = 'fas fa-moon';
                text.textContent = 'Modo escuro';
                localStorage.setItem('theme', 'light');
            }
        });
        
        // Aplicar tema salvo
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-theme');
                const themeToggle = document.getElementById('theme-toggle');
                themeToggle.querySelector('i').className = 'fas fa-sun';
                themeToggle.querySelector('span').textContent = 'Modo claro';
            }
        });
    </script>
</body>
</html>
"""
    
    # Criar o arquivo se não existir
    if not os.path.exists(caminho_template):
        with open(caminho_template, 'w', encoding='utf-8') as f:
            f.write(conteudo_template)
