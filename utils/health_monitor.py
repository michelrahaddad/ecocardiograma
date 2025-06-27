"""
Monitor de Saúde do Sistema
Monitoramento contínuo da integridade do banco de dados
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from utils.backup_security import create_manual_backup

logger = logging.getLogger('health_monitor')

class HealthMonitor:
    """Monitor de saúde do sistema de banco de dados"""
    
    def __init__(self):
        self.db_path = self.find_database()
        self.last_check = None
        
    def find_database(self):
        """Localizar arquivo do banco de dados"""
        possible_paths = [
            'ecocardiograma.db',
            'instance/ecocardiograma.db',
            '../ecocardiograma.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return 'ecocardiograma.db'
    
    def check_database_health(self):
        """Verificar saúde do banco de dados"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'database_exists': False,
            'database_accessible': False,
            'essential_tables_present': False,
            'data_integrity': False,
            'file_size': 0,
            'recommendations': []
        }
        
        try:
            # Verificar se o arquivo existe
            if os.path.exists(self.db_path):
                health_status['database_exists'] = True
                health_status['file_size'] = os.path.getsize(self.db_path)
                
                # Verificar se é muito pequeno (possível corrupção)
                if health_status['file_size'] < 1024:  # Menos de 1KB
                    health_status['recommendations'].append('Banco muito pequeno - possível corrupção')
            else:
                health_status['recommendations'].append('Arquivo do banco não encontrado')
                return health_status
            
            # Tentar conectar ao banco
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            health_status['database_accessible'] = True
            
            # Verificar tabelas essenciais
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            essential_tables = ['exames', 'parametros_ecocardiograma', 'medicos']
            missing_tables = [table for table in essential_tables if table not in tables]
            
            if not missing_tables:
                health_status['essential_tables_present'] = True
            else:
                health_status['recommendations'].append(f'Tabelas faltantes: {", ".join(missing_tables)}')
            
            # Verificar integridade dos dados
            try:
                # Verificar se há exames
                cursor.execute("SELECT COUNT(*) FROM exames")
                exam_count = cursor.fetchone()[0]
                
                # Verificar se há médicos
                cursor.execute("SELECT COUNT(*) FROM medicos")
                doctor_count = cursor.fetchone()[0]
                
                if exam_count > 0 or doctor_count > 0:
                    health_status['data_integrity'] = True
                else:
                    health_status['recommendations'].append('Banco sem dados importantes')
                
                # Verificar integridade SQLite
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result != 'ok':
                    health_status['recommendations'].append(f'Problema de integridade: {integrity_result}')
                    health_status['data_integrity'] = False
                
            except Exception as e:
                health_status['recommendations'].append(f'Erro na verificação de dados: {str(e)}')
            
            conn.close()
            
        except Exception as e:
            health_status['recommendations'].append(f'Erro ao acessar banco: {str(e)}')
            logger.error(f"Erro na verificação de saúde: {str(e)}")
        
        # Atualizar último check
        self.last_check = datetime.now()
        
        # Determinar se precisa de backup de emergência
        if not health_status['data_integrity'] or health_status['recommendations']:
            health_status['recommendations'].append('Recomendado criar backup imediatamente')
        
        return health_status
    
    def auto_backup_if_needed(self, health_status):
        """Criar backup automático se necessário"""
        needs_backup = (
            not health_status['data_integrity'] or
            'corrupção' in ' '.join(health_status['recommendations']).lower() or
            'problema de integridade' in ' '.join(health_status['recommendations']).lower()
        )
        
        if needs_backup:
            try:
                backup_path = create_manual_backup()
                if backup_path:
                    logger.warning(f"Backup de emergência criado devido a problemas: {backup_path}")
                    return backup_path
            except Exception as e:
                logger.error(f"Falha ao criar backup de emergência: {str(e)}")
        
        return None
    
    def get_system_stats(self):
        """Obter estatísticas do sistema"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'database_path': self.db_path,
            'database_size_mb': 0,
            'last_health_check': self.last_check.isoformat() if self.last_check else None
        }
        
        try:
            if os.path.exists(self.db_path):
                stats['database_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
                stats['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(self.db_path)
                ).isoformat()
            
            # Informações de espaço em disco
            disk_usage = os.statvfs('.')
            free_space_gb = (disk_usage.f_bavail * disk_usage.f_frsize) / (1024**3)
            total_space_gb = (disk_usage.f_blocks * disk_usage.f_frsize) / (1024**3)
            
            stats['disk_free_gb'] = round(free_space_gb, 2)
            stats['disk_total_gb'] = round(total_space_gb, 2)
            stats['disk_usage_percent'] = round(((total_space_gb - free_space_gb) / total_space_gb) * 100, 1)
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
        
        return stats

# Instância global
health_monitor = HealthMonitor()

def quick_health_check():
    """Verificação rápida de saúde"""
    return health_monitor.check_database_health()

def get_system_statistics():
    """Obter estatísticas do sistema"""
    return health_monitor.get_system_stats()