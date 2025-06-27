"""
Sistema de Segurança e Backup Automático do Banco de Dados
Sistema avançado para proteção contra perda de dados médicos críticos
"""

import os
import shutil
import hashlib
import time
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread

# Configuração de logging específico para segurança
security_logger = logging.getLogger('database_security')
security_handler = logging.FileHandler('logs/database_security.log')
security_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

class DatabaseSecurity:
    """Sistema de segurança e backup do banco de dados"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = Path("backups/automatic")
        self.logs_dir = Path("logs")
        self.max_backups = 30  # Manter 30 backups automáticos
        self.backup_interval_hours = 6  # Backup a cada 6 horas
        
        # Criar diretórios necessários
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar scheduler de backup automático
        self._setup_automatic_backup()
        
    def _setup_automatic_backup(self):
        """Configurar backup automático"""
        # Backup a cada 6 horas
        schedule.every(self.backup_interval_hours).hours.do(self._run_automatic_backup)
        
        # Backup diário às 02:00 (horário de Brasília)
        schedule.every().day.at("02:00").do(self._run_daily_backup)
        
        # Limpeza semanal de backups antigos (domingo às 03:00)
        schedule.every().sunday.at("03:00").do(self._cleanup_old_backups)
        
        # Verificação de integridade diária (às 01:00)
        schedule.every().day.at("01:00").do(self._verify_database_integrity)
        
    def start_background_scheduler(self):
        """Iniciar scheduler em background"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        security_logger.info("Scheduler de backup automático iniciado")
        
    def _run_automatic_backup(self):
        """Executar backup automático"""
        try:
            backup_path = self.create_backup(backup_type="AUTOMATICO")
            security_logger.info(f"Backup automático criado: {backup_path}")
            
            # Verificar integridade do backup
            if self._verify_backup_integrity(backup_path):
                security_logger.info(f"Backup automático verificado com sucesso: {backup_path}")
            else:
                security_logger.error(f"Falha na verificação do backup: {backup_path}")
                
        except Exception as e:
            security_logger.error(f"Erro no backup automático: {str(e)}")
            
    def _run_daily_backup(self):
        """Executar backup diário"""
        try:
            backup_path = self.create_backup(backup_type="DIARIO")
            security_logger.info(f"Backup diário criado: {backup_path}")
            
            # Criar também backup JSON dos dados críticos
            json_backup = self._create_json_backup()
            security_logger.info(f"Backup JSON criado: {json_backup}")
            
        except Exception as e:
            security_logger.error(f"Erro no backup diário: {str(e)}")
            
    def create_backup(self, backup_type="MANUAL"):
        """Criar backup do banco de dados"""
        timestamp = datetime_brasilia().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{backup_type.lower()}_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Obter caminho do banco atual
            db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if db_uri.startswith('sqlite:///'):
                # SQLite - cópia direta do arquivo
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)
                else:
                    raise FileNotFoundError(f"Arquivo do banco não encontrado: {db_path}")
                    
            elif db_uri.startswith('postgresql://'):
                # PostgreSQL - usar pg_dump se disponível
                self._create_postgresql_backup(backup_path)
                
            else:
                raise ValueError(f"Tipo de banco não suportado: {db_uri}")
            
            # Calcular hash do backup para verificação
            backup_hash = self._calculate_file_hash(backup_path)
            
            # Salvar informações do backup
            backup_info = {
                'filename': backup_filename,
                'path': str(backup_path),
                'timestamp': timestamp,
                'type': backup_type,
                'size': backup_path.stat().st_size,
                'hash': backup_hash,
                'created_at': datetime_brasilia().isoformat()
            }
            
            # Salvar metadados
            info_path = backup_path.with_suffix('.info.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            security_logger.info(f"Backup criado com sucesso: {backup_path} ({backup_info['size']} bytes)")
            return backup_path
            
        except Exception as e:
            security_logger.error(f"Erro ao criar backup: {str(e)}")
            raise
            
    def _create_postgresql_backup(self, backup_path):
        """Criar backup do PostgreSQL usando pg_dump"""
        import subprocess
        
        db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        try:
            # Executar pg_dump
            result = subprocess.run([
                'pg_dump', 
                '--no-password',
                '--format=custom',
                '--compress=9',
                '--file', str(backup_path),
                db_uri
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"pg_dump falhou: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout no backup do PostgreSQL")
        except FileNotFoundError:
            # pg_dump não disponível, usar método alternativo
            self._create_sql_dump_backup(backup_path)
            
    def _create_sql_dump_backup(self, backup_path):
        """Criar backup SQL usando SQLAlchemy"""
        with self.app.app_context():
            # Obter todas as tabelas
            tables = db.metadata.tables.keys()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(f"-- Backup do banco de dados criado em {datetime_brasilia().isoformat()}\n\n")
                
                for table_name in tables:
                    # Exportar estrutura e dados da tabela
                    result = db.session.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    
                    if rows:
                        columns = result.keys()
                        f.write(f"-- Dados da tabela {table_name}\n")
                        
                        for row in rows:
                            values = []
                            for value in row:
                                if value is None:
                                    values.append('NULL')
                                elif isinstance(value, str):
                                    values.append(f"'{value.replace('\'', '\'\'')}'")
                                else:
                                    values.append(str(value))
                            
                            f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                        
                        f.write("\n")
                        
    def _create_json_backup(self):
        """Criar backup em formato JSON para dados críticos"""
        timestamp = datetime_brasilia().strftime('%Y%m%d_%H%M%S')
        json_backup_path = self.backup_dir / f"backup_json_{timestamp}.json"
        
        with self.app.app_context():
            backup_data = {
                'timestamp': datetime_brasilia().isoformat(),
                'version': '1.0',
                'data': {}
            }
            
            # Exportar dados das tabelas principais
            tables_to_backup = ['exames', 'parametros_ecocardiograma', 'laudos_ecocardiograma', 'medicos']
            
            for table_name in tables_to_backup:
                try:
                    result = db.session.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    backup_data['data'][table_name] = []
                    for row in rows:
                        row_dict = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            if isinstance(value, datetime):
                                row_dict[column] = value.isoformat()
                            else:
                                row_dict[column] = value
                        backup_data['data'][table_name].append(row_dict)
                        
                except Exception as e:
                    security_logger.warning(f"Erro ao exportar tabela {table_name}: {str(e)}")
                    
            # Salvar JSON
            with open(json_backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
            security_logger.info(f"Backup JSON criado: {json_backup_path}")
            return json_backup_path
            
    def _calculate_file_hash(self, file_path):
        """Calcular hash SHA256 do arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
        
    def _verify_backup_integrity(self, backup_path):
        """Verificar integridade do backup"""
        try:
            # Verificar se o arquivo existe e não está vazio
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                return False
                
            # Para SQLite, tentar abrir o banco
            if backup_path.suffix == '.db':
                conn = sqlite3.connect(str(backup_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                # Verificar se há tabelas
                return len(tables) > 0
                
            return True
            
        except Exception as e:
            security_logger.error(f"Erro na verificação de integridade: {str(e)}")
            return False
            
    def _verify_database_integrity(self):
        """Verificar integridade do banco principal"""
        try:
            with self.app.app_context():
                # Verificar conexão
                db.session.execute(text("SELECT 1"))
                
                # Verificar tabelas principais
                essential_tables = ['exames', 'parametros_ecocardiograma', 'medicos']
                for table in essential_tables:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    security_logger.info(f"Tabela {table}: {count} registros")
                
                security_logger.info("Verificação de integridade concluída com sucesso")
                return True
                
        except Exception as e:
            security_logger.error(f"Erro na verificação de integridade do banco: {str(e)}")
            # Em caso de erro crítico, tentar backup de emergência
            self._emergency_backup()
            return False
            
    def _emergency_backup(self):
        """Criar backup de emergência"""
        try:
            emergency_path = self.create_backup(backup_type="EMERGENCIA")
            security_logger.critical(f"Backup de emergência criado: {emergency_path}")
        except Exception as e:
            security_logger.critical(f"FALHA CRÍTICA: Não foi possível criar backup de emergência: {str(e)}")
            
    def _cleanup_old_backups(self):
        """Limpar backups antigos"""
        try:
            # Listar todos os backups
            backup_files = list(self.backup_dir.glob("backup_*.db"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Manter apenas os backups mais recentes
            if len(backup_files) > self.max_backups:
                for old_backup in backup_files[self.max_backups:]:
                    old_backup.unlink()
                    # Remover também o arquivo .info.json se existir
                    info_file = old_backup.with_suffix('.info.json')
                    if info_file.exists():
                        info_file.unlink()
                    security_logger.info(f"Backup antigo removido: {old_backup}")
                    
            security_logger.info(f"Limpeza de backups concluída. Mantidos {min(len(backup_files), self.max_backups)} backups")
            
        except Exception as e:
            security_logger.error(f"Erro na limpeza de backups: {str(e)}")
            
    def restore_backup(self, backup_path):
        """Restaurar backup do banco de dados"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
                
            # Verificar integridade antes de restaurar
            if not self._verify_backup_integrity(Path(backup_path)):
                raise ValueError("Backup corrompido ou inválido")
                
            # Criar backup do estado atual antes de restaurar
            current_backup = self.create_backup(backup_type="PRE_RESTAURACAO")
            security_logger.info(f"Backup do estado atual criado: {current_backup}")
            
            # Restaurar dependendo do tipo de banco
            db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                shutil.copy2(backup_path, db_path)
                
            elif db_uri.startswith('postgresql://'):
                # Usar pg_restore para PostgreSQL
                self._restore_postgresql_backup(backup_path)
                
            security_logger.info(f"Banco de dados restaurado com sucesso a partir de: {backup_path}")
            return True
            
        except Exception as e:
            security_logger.error(f"Erro ao restaurar backup: {str(e)}")
            raise
            
    def _restore_postgresql_backup(self, backup_path):
        """Restaurar backup do PostgreSQL"""
        import subprocess
        
        db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        try:
            result = subprocess.run([
                'pg_restore',
                '--clean',
                '--if-exists',
                '--no-owner',
                '--no-privileges',
                '--dbname', db_uri,
                backup_path
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                raise RuntimeError(f"pg_restore falhou: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout na restauração do PostgreSQL")
            
    def get_backup_status(self):
        """Obter status dos backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.db"):
            info_file = backup_file.with_suffix('.info.json')
            
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                    backups.append(backup_info)
                except:
                    # Se não conseguir ler o arquivo de info, criar info básica
                    stat = backup_file.stat()
                    backups.append({
                        'filename': backup_file.name,
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'UNKNOWN'
                    })
                    
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
        
    def monitor_disk_space(self):
        """Monitorar espaço em disco"""
        try:
            disk_usage = shutil.disk_usage(self.backup_dir)
            free_space_gb = disk_usage.free / (1024**3)
            
            if free_space_gb < 1.0:  # Menos de 1GB livre
                security_logger.warning(f"Pouco espaço em disco: {free_space_gb:.2f}GB livres")
                # Limpar backups antigos automaticamente
                self._cleanup_old_backups()
                
            return {
                'free_space_gb': free_space_gb,
                'total_space_gb': disk_usage.total / (1024**3),
                'used_space_gb': disk_usage.used / (1024**3)
            }
            
        except Exception as e:
            security_logger.error(f"Erro ao verificar espaço em disco: {str(e)}")
            return None

# Instância global do sistema de segurança
database_security = None

def init_database_security(app):
    """Inicializar sistema de segurança do banco"""
    global database_security
    database_security = DatabaseSecurity(app)
    database_security.start_background_scheduler()
    return database_security