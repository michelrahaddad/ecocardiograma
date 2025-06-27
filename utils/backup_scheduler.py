"""
Sistema de Backup Automático - Scheduler
Gerencia backup automático diário com agendamento interno
"""

import os
import time
import threading
from datetime import datetime, timedelta
from utils.backup_security import create_daily_backup
import logging

logger = logging.getLogger('backup_scheduler')

class BackupScheduler:
    """Agendador de backup automático"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.backup_time = "02:00"  # Horário padrão
        self.enabled = True
        
    def set_backup_time(self, time_str):
        """Define horário do backup (formato HH:MM)"""
        self.backup_time = time_str
        logger.info(f"Horário de backup definido para: {time_str}")
    
    def enable_auto_backup(self, enabled=True):
        """Ativa/desativa backup automático"""
        self.enabled = enabled
        logger.info(f"Backup automático {'ativado' if enabled else 'desativado'}")
    
    def _get_next_backup_time(self):
        """Calcula próximo horário de backup"""
        now = datetime.now()
        hour, minute = map(int, self.backup_time.split(':'))
        
        # Próximo backup hoje
        next_backup = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Se já passou da hora hoje, agendar para amanhã
        if next_backup <= now:
            next_backup += timedelta(days=1)
        
        return next_backup
    
    def _backup_loop(self):
        """Loop principal do agendador"""
        logger.info("Scheduler de backup iniciado")
        
        while self.running:
            try:
                if not self.enabled:
                    time.sleep(3600)  # Verificar a cada hora se foi reativado
                    continue
                
                next_backup = self._get_next_backup_time()
                now = datetime.now()
                
                # Calcular tempo até próximo backup
                time_until_backup = (next_backup - now).total_seconds()
                
                if time_until_backup > 0:
                    logger.info(f"Próximo backup agendado para: {next_backup.strftime('%d/%m/%Y às %H:%M')}")
                    
                    # Dormir até a hora do backup (verificar a cada 30 min)
                    sleep_time = min(time_until_backup, 1800)  # máximo 30 minutos
                    time.sleep(sleep_time)
                    continue
                
                # Hora do backup!
                logger.info("Iniciando backup automático...")
                success = create_daily_backup()
                
                if success:
                    logger.info("Backup automático concluído com sucesso")
                else:
                    logger.error("Falha no backup automático")
                
                # Aguardar 70 segundos para evitar execução dupla
                time.sleep(70)
                
            except Exception as e:
                logger.error(f"Erro no scheduler de backup: {e}")
                time.sleep(300)  # Aguardar 5 minutos antes de tentar novamente
    
    def start(self):
        """Inicia o agendador"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.thread.start()
        logger.info("Agendador de backup automático iniciado")
    
    def stop(self):
        """Para o agendador"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Agendador de backup automático parado")
    
    def get_status(self):
        """Retorna status do agendador"""
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'Backup automático desativado',
                'next_backup': None
            }
        
        if not self.running:
            return {
                'status': 'stopped',
                'message': 'Agendador parado',
                'next_backup': None
            }
        
        next_backup = self._get_next_backup_time()
        return {
            'status': 'running',
            'message': 'Backup automático ativo',
            'next_backup': next_backup.strftime('%d/%m/%Y às %H:%M'),
            'backup_time': self.backup_time
        }

# Instância global do agendador
backup_scheduler = BackupScheduler()

def init_backup_scheduler():
    """Inicializa o agendador de backup"""
    backup_scheduler.start()

def get_backup_scheduler():
    """Retorna a instância do agendador"""
    return backup_scheduler