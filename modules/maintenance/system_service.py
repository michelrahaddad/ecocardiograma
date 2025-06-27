"""
Serviço de Sistema - Manutenção e monitoramento

Centraliza todas as operações de manutenção, monitoramento
e diagnóstico do sistema.
"""

from typing import Dict, List, Any
from datetime import datetime
import os
import psutil
from modules.core.database import DatabaseManager
from modules.core.exceptions import BusinessRuleError

class SystemService:
    """Serviço de manutenção e monitoramento do sistema"""
    
    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Obtém status geral do sistema"""
        try:
            # Status do banco de dados
            db_status = SystemService._check_database_health()
            
            # Status do sistema
            system_status = SystemService._get_system_metrics()
            
            # Status da aplicação
            app_status = SystemService._get_application_status()
            
            return {
                'database': db_status,
                'system': system_status,
                'application': app_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise BusinessRuleError(f"Erro ao obter status do sistema: {str(e)}")
    
    @staticmethod
    def _check_database_health() -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        try:
            from models import Exame
            
            # Teste de conectividade
            total_exams = DatabaseManager.execute_query(
                lambda: Exame.query.count()
            )
            
            return {
                'status': 'healthy',
                'total_records': total_exams,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    @staticmethod
    def _get_system_metrics() -> Dict[str, Any]:
        """Obtém métricas do sistema"""
        try:
            # Uso de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Uso de memória
            memory = psutil.virtual_memory()
            
            # Uso de disco
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'core_count': psutil.cpu_count()
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2)
                }
            }
            
        except Exception:
            return {
                'cpu': {'usage_percent': 0, 'core_count': 1},
                'memory': {'total_gb': 0, 'used_gb': 0, 'usage_percent': 0},
                'disk': {'total_gb': 0, 'used_gb': 0, 'usage_percent': 0}
            }
    
    @staticmethod
    def _get_application_status() -> Dict[str, Any]:
        """Obtém status da aplicação"""
        try:
            from modules.exams.exam_service import ExamService
            
            # Estatísticas básicas
            stats = ExamService.get_exam_statistics()
            
            return {
                'status': 'running',
                'version': '2.0.0',
                'statistics': stats,
                'uptime': SystemService._get_uptime()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'version': '2.0.0'
            }
    
    @staticmethod
    def _get_uptime() -> str:
        """Calcula tempo de atividade do sistema"""
        try:
            uptime_seconds = psutil.boot_time()
            uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
            return str(uptime).split('.')[0]  # Remove microsegundos
        except Exception:
            return "Indisponível"