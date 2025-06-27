# Documentação Técnica - Sistema de Ecocardiograma

## Visão Geral do Sistema

Sistema de gerenciamento de exames de ecocardiograma desenvolvido para o Grupo Vidah. Oferece funcionalidades completas para criação, edição, visualização e geração de relatórios médicos profissionais com assinatura digital.

## Arquitetura do Sistema

### Estrutura de Diretórios
```
/
├── app.py                 # Configuração principal da aplicação Flask
├── main.py               # Ponto de entrada da aplicação
├── models.py             # Modelos de dados SQLAlchemy
├── routes.py            # Rotas principais (em refatoração)
├── auth/                # Sistema de autenticação modular
│   ├── models.py        # Modelo AuthUser
│   ├── services.py      # Serviços de autenticação
│   ├── decorators.py    # Decorators de segurança
│   └── validators.py    # Validações de entrada
├── modules/             # Módulos organizados
│   └── routes/          # Rotas refatoradas
│       └── exam_routes.py # Lógica de exames
├── utils/               # Utilitários do sistema
│   ├── pdf_generator_fixed.py # Geração de PDFs
│   ├── logging_system.py     # Sistema de logs
│   └── backup.py            # Sistema de backup
├── tests/               # Testes automatizados
│   ├── test_authentication.py
│   └── test_pdf_generation.py
└── templates/           # Templates HTML Jinja2
```

### Tecnologias Utilizadas

- **Backend**: Flask 2.3+ com SQLAlchemy
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Autenticação**: Flask-Login com sistema AuthUser customizado
- **PDFs**: ReportLab para geração de relatórios médicos
- **Frontend**: Bootstrap 5.1.3, jQuery, FontAwesome
- **Servidor**: Gunicorn com configuração para produção

## Funcionalidades Principais

### 1. Gerenciamento de Exames
- **Criação**: Formulário completo com validação anti-duplicata
- **Edição**: Atualização de dados básicos e parâmetros
- **Visualização**: Interface responsiva para consulta
- **Exclusão**: Remoção segura com logs de auditoria

### 2. Sistema de Autenticação
- **Login Seguro**: Hash de senhas com salt
- **Controle de Acesso**: Níveis user/admin
- **Rate Limiting**: Proteção contra ataques de força bruta
- **Auditoria**: Logs de todas as ações críticas

### 3. Geração de PDFs
- **Layout Profissional**: Formato A4 com cabeçalho/rodapé
- **Assinatura Digital**: Integração automática com base de médicos
- **Dados Completos**: Inclusão de todos os parâmetros e laudos
- **Otimização**: Compressão e qualidade controlada

## Configuração e Deploy

### Variáveis de Ambiente
```bash
DATABASE_URL=sqlite:///ecocardiograma.db
SESSION_SECRET=chave_secreta_sessoes
FLASK_ENV=production
```

### Configuração de Produção
```bash
# Iniciar aplicação
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## Testes Automatizados

### Executar Testes
```bash
# Todos os testes
python -m pytest tests/

# Teste específico
python -m pytest tests/test_authentication.py -v
```

Versão atual: **2.1.0** (Junho 2025)