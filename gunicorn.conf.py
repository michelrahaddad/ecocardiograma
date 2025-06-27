# Configuração do Gunicorn para Sistema de Ecocardiograma
import os

# Configuração do servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))

# Configurações de timeout
timeout = 120
keepalive = 5

# Configurações de memória
max_requests = 1000
max_requests_jitter = 100

# Configurações de worker
worker_class = "sync"
worker_connections = 1000

# Configurações de logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Configurações de processo
preload_app = True
daemon = False

# Configurações específicas para produção
def when_ready(server):
    server.log.info("Servidor Grupo Vidah iniciado")

def worker_int(worker):
    worker.log.info("Worker interrompido")

def pre_fork(server, worker):
    server.log.info("Worker iniciando")

def post_fork(server, worker):
    server.log.info("Worker iniciado")

def worker_abort(worker):
    worker.log.info("Worker abortado")

# Configurações de segurança
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}