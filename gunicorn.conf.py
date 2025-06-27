import os

# Configuração do servidor
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
preload_app = True
max_requests = 1000
max_requests_jitter = 100

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s - - [%(t)s] "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Configurações de worker
worker_tmp_dir = "/dev/shm"
forwarded_allow_ips = "*"

# Hooks do servidor
def when_ready(server):
    server.log.info("Servidor Grupo Vidah iniciado")

def worker_int(worker):
    server.log.info("Worker interrompido pelo usuário")

def pre_fork(server, worker):
    server.log.info("Worker iniciando")

def post_fork(server, worker):
    server.log.info("Worker iniciado")

def worker_abort(worker):
    server.log.info("Worker abortado")
