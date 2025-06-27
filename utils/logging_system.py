"""
Sistema de Logging Centralizado - Sistema de Ecocardiograma

Módulo para registrar todas as atividades críticas do sistema
com integração ao banco de dados e fuso horário de Brasília.
"""

import logging
import traceback
from datetime import datetime
from pytz import timezone
from sqlalchemy.exc import SQLAlchemyError
from flask import request, session, g


def datetime_brasilia():
    """Retorna datetime atual no fuso horário de Brasília (UTC-3)"""
    brasilia_tz = timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz).replace(tzinfo=None)


class DatabaseLogHandler(logging.Handler):
    """Handler personalizado para salvar logs no banco de dados"""
    
    def __init__(self, app=None, db=None):
        super().__init__()
        self.app = app
        self.db = db
        
    def emit(self, record):
        """Salva o log no banco de dados"""
        try:
            if self.app and self.db:
                with self.app.app_context():
                    from models import LogSistema
                    
                    # Obter informações do usuário se disponível
                    usuario_id = None
                    if hasattr(g, 'current_user') and hasattr(g.current_user, 'id'):
                        usuario_id = g.current_user.id
                    elif 'medico_selecionado' in session:
                        # Para médicos do sistema
                        usuario_id = session.get('medico_selecionado')
                    
                    # Criar entrada de log
                    log_entry = LogSistema(
                        nivel=record.levelname,
                        mensagem=self.format(record),
                        modulo=record.module,
                        usuario_id=usuario_id,
                        created_at=datetime_brasilia()
                    )
                    
                    self.db.session.add(log_entry)
                    self.db.session.commit()
                    
        except Exception as e:
            # Em caso de erro, registra no log padrão
            print(f"Erro ao salvar log no banco: {str(e)}")


def configurar_logging(app, db):
    """Configura o sistema de logging centralizado"""
    
    # Configurar logger principal
    logger = logging.getLogger('ecocardiograma_system')
    logger.setLevel(logging.DEBUG)
    
    # Remover handlers existentes
    logger.handlers.clear()
    
    # Formatter personalizado
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para banco de dados
    db_handler = DatabaseLogHandler(app, db)
    db_handler.setLevel(logging.INFO)
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    
    # Handler para console (desenvolvimento)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_system_event(nivel, mensagem, modulo='system', detalhes=None):
    """
    Registra evento do sistema de forma centralizada
    
    Args:
        nivel: INFO, WARNING, ERROR, DEBUG
        mensagem: Mensagem principal do log
        modulo: Módulo/componente que gerou o log
        detalhes: Informações adicionais (opcional)
    """
    logger = logging.getLogger('ecocardiograma_system')
    
    # Adicionar detalhes da requisição se disponível
    request_info = ""
    if request:
        request_info = f" | IP: {request.remote_addr} | URL: {request.path}"
    
    # Montar mensagem completa
    mensagem_completa = f"{mensagem}{request_info}"
    if detalhes:
        mensagem_completa += f" | Detalhes: {detalhes}"
    
    # Registrar no nível apropriado
    if nivel == 'DEBUG':
        logger.debug(mensagem_completa)
    elif nivel == 'INFO':
        logger.info(mensagem_completa)
    elif nivel == 'WARNING':
        logger.warning(mensagem_completa)
    elif nivel == 'ERROR':
        logger.error(mensagem_completa)


def log_database_operation(operacao, tabela, registro_id=None, sucesso=True, erro=None):
    """Registra operações de banco de dados"""
    if sucesso:
        log_system_event(
            'INFO',
            f'Operação de banco: {operacao}',
            'database',
            f'Tabela: {tabela}, ID: {registro_id}'
        )
    else:
        log_system_event(
            'ERROR',
            f'Erro em operação de banco: {operacao}',
            'database',
            f'Tabela: {tabela}, ID: {registro_id}, Erro: {erro}'
        )


def log_user_action(acao, detalhes=None):
    """Registra ações dos usuários"""
    log_system_event(
        'INFO',
        f'Ação do usuário: {acao}',
        'user_action',
        detalhes
    )


def log_pdf_generation(exame_id, sucesso=True, erro=None):
    """Registra geração de PDFs"""
    if sucesso:
        log_system_event(
            'INFO',
            f'PDF gerado com sucesso para exame {exame_id}',
            'pdf_generator'
        )
    else:
        log_system_event(
            'ERROR',
            f'Erro na geração de PDF para exame {exame_id}',
            'pdf_generator',
            f'Erro: {erro}'
        )


def log_backup_operation(tipo_backup, sucesso=True, erro=None, detalhes=None):
    """Registra operações de backup"""
    if sucesso:
        log_system_event(
            'INFO',
            f'Backup {tipo_backup} realizado com sucesso',
            'backup_system',
            detalhes
        )
    else:
        log_system_event(
            'ERROR',
            f'Erro no backup {tipo_backup}',
            'backup_system',
            f'Erro: {erro}, Detalhes: {detalhes}'
        )


def log_system_startup():
    """Registra inicialização do sistema"""
    log_system_event(
        'INFO',
        'Sistema de Ecocardiograma iniciado',
        'system_startup',
        f'Timestamp: {datetime_brasilia()}'
    )


def log_error_with_traceback(erro, modulo='system'):
    """Registra erros com traceback completo"""
    traceback_str = traceback.format_exc()
    log_system_event(
        'ERROR',
        f'Erro capturado: {str(erro)}',
        modulo,
        f'Traceback: {traceback_str}'
    )


def log_security_event(evento, detalhes=None):
    """Registra eventos de segurança"""
    log_system_event(
        'WARNING',
        f'Evento de segurança: {evento}',
        'security',
        detalhes
    )


def log_performance_metric(operacao, tempo_execucao, detalhes=None):
    """Registra métricas de performance"""
    log_system_event(
        'DEBUG',
        f'Performance: {operacao} executado em {tempo_execucao:.3f}s',
        'performance',
        detalhes
    )


def log_calculation_result(tipo_calculo, parametros, resultado):
    """Registra resultados de cálculos médicos"""
    log_system_event(
        'DEBUG',
        f'Cálculo médico: {tipo_calculo}',
        'medical_calculations',
        f'Parâmetros: {parametros}, Resultado: {resultado}'
    )


# Decorator para log automático de funções
def log_function_call(nivel='INFO', modulo='function_call'):
    """Decorator para registrar automaticamente chamadas de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                start_time = datetime_brasilia()
                resultado = func(*args, **kwargs)
                end_time = datetime_brasilia()
                
                tempo_execucao = (end_time - start_time).total_seconds()
                
                log_system_event(
                    nivel,
                    f'Função {func.__name__} executada com sucesso',
                    modulo,
                    f'Tempo: {tempo_execucao:.3f}s'
                )
                
                return resultado
                
            except Exception as e:
                log_error_with_traceback(e, modulo)
                raise
                
        return wrapper
    return decorator


# Context manager para logging de operações
class LoggedOperation:
    """Context manager para operações com logging automático"""
    
    def __init__(self, operacao, modulo='operation'):
        self.operacao = operacao
        self.modulo = modulo
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime_brasilia()
        log_system_event(
            'INFO',
            f'Iniciando operação: {self.operacao}',
            self.modulo
        )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime_brasilia()
        tempo_execucao = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            log_system_event(
                'INFO',
                f'Operação concluída: {self.operacao}',
                self.modulo,
                f'Tempo: {tempo_execucao:.3f}s'
            )
        else:
            log_system_event(
                'ERROR',
                f'Operação falhou: {self.operacao}',
                self.modulo,
                f'Erro: {exc_val}, Tempo: {tempo_execucao:.3f}s'
            )