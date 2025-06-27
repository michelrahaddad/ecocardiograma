"""
Sistema de Backup Automático Simples e Seguro
Proteção contra perda de dados sem quebrar o sistema atual
"""

import os
import shutil
import hashlib
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuração de logging
logger = logging.getLogger('backup_security')

class SimpleBackupSystem:
    """Sistema de backup simples e confiável"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Subdiretórios organizados
        self.daily_dir = self.backup_dir / "daily"
        self.manual_dir = self.backup_dir / "manual"
        self.emergency_dir = self.backup_dir / "emergency"
        
        for directory in [self.daily_dir, self.manual_dir, self.emergency_dir]:
            directory.mkdir(exist_ok=True)
    
    def get_database_path(self):
        """Obter caminho do banco de dados atual"""
        # Verificar se existe o arquivo SQLite padrão
        possible_paths = [
            'ecocardiograma.db',
            'instance/ecocardiograma.db',
            '../ecocardiograma.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Se não encontrar, usar o padrão
        return 'ecocardiograma.db'
    
    def create_backup(self, backup_type="MANUAL"):
        """Criar backup do banco de dados"""
        try:
            db_path = self.get_database_path()
            
            if not os.path.exists(db_path):
                logger.warning(f"Banco de dados não encontrado em: {db_path}")
                return None
            
            # Definir diretório baseado no tipo
            if backup_type == "DAILY":
                target_dir = self.daily_dir
            elif backup_type == "EMERGENCY":
                target_dir = self.emergency_dir
            else:
                target_dir = self.manual_dir
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{backup_type.lower()}_{timestamp}.db"
            backup_path = target_dir / backup_filename
            
            # Copiar arquivo do banco
            shutil.copy2(db_path, backup_path)
            
            # Verificar se o backup foi criado corretamente
            if self.verify_backup(backup_path):
                # Criar arquivo de informações
                info = {
                    'filename': backup_filename,
                    'type': backup_type,
                    'created_at': datetime.now().isoformat(),
                    'size_bytes': backup_path.stat().st_size,
                    'source_path': db_path,
                    'hash': self.calculate_hash(backup_path)
                }
                
                info_path = backup_path.with_suffix('.json')
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Backup criado: {backup_path} ({info['size_bytes']} bytes)")
                return backup_path
            else:
                logger.error(f"Backup corrompido, removendo: {backup_path}")
                backup_path.unlink()
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return None
    
    def verify_backup(self, backup_path):
        """Verificar se o backup está íntegro"""
        try:
            # Verificar se o arquivo existe e não está vazio
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                return False
            
            # Tentar abrir como SQLite
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            
            # Verificar se há tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Verificar tabelas essenciais
            table_names = [table[0] for table in tables]
            essential_tables = ['exames', 'parametros_ecocardiograma']
            
            has_essential = any(table in table_names for table in essential_tables)
            
            conn.close()
            
            return has_essential and len(tables) > 0
            
        except Exception as e:
            logger.error(f"Erro na verificação do backup: {str(e)}")
            return False
    
    def calculate_hash(self, file_path):
        """Calcular hash SHA256 do arquivo"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return None
    
    def create_daily_backup(self):
        """Criar backup diário"""
        backup_path = self.create_backup("DAILY")
        if backup_path:
            # Limpar backups diários antigos (manter apenas 7 dias)
            self.cleanup_old_backups(self.daily_dir, days_to_keep=7)
        return backup_path
    
    def create_emergency_backup(self):
        """Criar backup de emergência"""
        return self.create_backup("EMERGENCY")
    
    def cleanup_old_backups(self, directory, days_to_keep=7):
        """Limpar backups antigos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for backup_file in directory.glob("backup_*.db"):
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    # Remover arquivo de backup
                    backup_file.unlink()
                    
                    # Remover arquivo de informações se existir
                    info_file = backup_file.with_suffix('.json')
                    if info_file.exists():
                        info_file.unlink()
                    
                    logger.info(f"Backup antigo removido: {backup_file}")
                    
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {str(e)}")
    
    def list_backups(self):
        """Listar todos os backups disponíveis"""
        backups = []
        
        for directory in [self.daily_dir, self.manual_dir, self.emergency_dir]:
            for backup_file in directory.glob("backup_*.db"):
                info_file = backup_file.with_suffix('.json')
                
                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            backup_info = json.load(f)
                        backup_info['path'] = str(backup_file)
                        backups.append(backup_info)
                    except:
                        # Se não conseguir ler o JSON, criar info básica
                        stat = backup_file.stat()
                        backups.append({
                            'filename': backup_file.name,
                            'path': str(backup_file),
                            'type': 'UNKNOWN',
                            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'size_bytes': stat.st_size
                        })
        
        # Ordenar por data de criação (mais recente primeiro)
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def restore_backup(self, backup_path):
        """Restaurar backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup não encontrado: {backup_path}")
                return False
            
            # Verificar integridade do backup
            if not self.verify_backup(Path(backup_path)):
                logger.error(f"Backup corrompido: {backup_path}")
                return False
            
            # Criar backup do estado atual
            current_backup = self.create_backup("PRE_RESTAURACAO")
            if current_backup:
                logger.info(f"Backup do estado atual criado: {current_backup}")
            
            # Restaurar o backup
            db_path = self.get_database_path()
            shutil.copy2(backup_path, db_path)
            
            logger.info(f"Banco restaurado com sucesso de: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return False
    
    def get_backup_statistics(self):
        """Obter estatísticas dos backups"""
        backups = self.list_backups()
        
        stats = {
            'total_backups': len(backups),
            'total_size_bytes': sum(b.get('size_bytes', 0) for b in backups),
            'by_type': {},
            'oldest_backup': None,
            'newest_backup': None
        }
        
        if backups:
            stats['newest_backup'] = backups[0]['created_at']
            stats['oldest_backup'] = backups[-1]['created_at']
            
            # Contar por tipo
            for backup in backups:
                backup_type = backup.get('type', 'UNKNOWN')
                stats['by_type'][backup_type] = stats['by_type'].get(backup_type, 0) + 1
        
        return stats

# Instância global
backup_system = SimpleBackupSystem()

def create_manual_backup():
    """Função simples para criar backup manual"""
    return backup_system.create_backup("MANUAL")

def create_daily_backup():
    """Função simples para criar backup diário"""
    return backup_system.create_daily_backup()

def get_backup_list():
    """Função simples para listar backups"""
    return backup_system.list_backups()

def restore_from_backup(backup_path):
    """Função simples para restaurar backup"""
    return backup_system.restore_backup(backup_path)