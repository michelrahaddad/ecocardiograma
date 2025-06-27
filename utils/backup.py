"""
Sistema de Ecocardiograma - Grupo Vidah
Sistema de Backup e Restauração
"""

import os
import json
import sqlite3
import zipfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
import tempfile
import hashlib
from typing import Dict, List, Optional, Tuple

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupManager:
    """Gerenciador de backup e restauração do sistema"""
    
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = os.path.join(os.getcwd(), 'backups')
        self.temp_dir = tempfile.gettempdir()
        
        # Criar diretório de backup se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Configurações padrão
        self.config = {
            'max_backups': 10,
            'compression_level': 6,
            'include_generated_pdfs': False,
            'include_logs': True
        }
    
    def criar_backup(self, tipo_backup='COMPLETO', nome_customizado=None):
        """
        Cria um backup do sistema
        
        Args:
            tipo_backup: COMPLETO, INCREMENTAL, DADOS, CONFIGURACAO
            nome_customizado: Nome personalizado para o backup
            
        Returns:
            str: Caminho do arquivo de backup criado
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if nome_customizado:
                backup_filename = f"{nome_customizado}_{timestamp}.zip"
            else:
                backup_filename = f"backup_{tipo_backup.lower()}_{timestamp}.zip"
            
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            logger.info(f"Iniciando backup {tipo_backup}: {backup_filename}")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=self.config['compression_level']) as backup_zip:
                
                # Adicionar metadados do backup
                self._add_backup_metadata(backup_zip, tipo_backup)
                
                if tipo_backup == 'COMPLETO':
                    self._backup_completo(backup_zip)
                elif tipo_backup == 'INCREMENTAL':
                    self._backup_incremental(backup_zip)
                elif tipo_backup == 'DADOS':
                    self._backup_dados(backup_zip)
                elif tipo_backup == 'CONFIGURACAO':
                    self._backup_configuracao(backup_zip)
                else:
                    raise ValueError(f"Tipo de backup não suportado: {tipo_backup}")
            
            # Verificar integridade do backup
            if self._verificar_integridade_backup(backup_path):
                logger.info(f"Backup criado com sucesso: {backup_path}")
                
                # Limpar backups antigos se necessário
                self._limpar_backups_antigos()
                
                return backup_path
            else:
                raise Exception("Falha na verificação de integridade do backup")
                
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            # Remover arquivo de backup corrompido se existir
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def _add_backup_metadata(self, backup_zip, tipo_backup):
        """Adiciona metadados ao backup"""
        metadata = {
            'version': '2.1.0',
            'tipo_backup': tipo_backup,
            'timestamp': datetime.now().isoformat(),
            'sistema': 'Sistema de Ecocardiograma - Grupo Vidah',
            'database_type': 'SQLite',
            'files_included': [],
            'checksum': None
        }
        
        # Adicionar informações do sistema
        try:
            import platform
            metadata['system_info'] = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'hostname': platform.node()
            }
        except:
            pass
        
        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
        backup_zip.writestr('backup_metadata.json', metadata_json)
    
    def _backup_completo(self, backup_zip):
        """Realiza backup completo do sistema"""
        logger.info("Executando backup completo...")
        
        # Backup do banco de dados
        self._backup_database(backup_zip)
        
        # Backup dos arquivos de configuração
        self._backup_config_files(backup_zip)
        
        # Backup de templates e assets
        self._backup_templates_assets(backup_zip)
        
        # Backup de arquivos Python
        self._backup_python_files(backup_zip)
        
        # Backup de assinaturas digitais
        self._backup_signatures(backup_zip)
        
        # Backup de PDFs gerados (opcional)
        if self.config['include_generated_pdfs']:
            self._backup_generated_pdfs(backup_zip)
        
        # Backup de logs (opcional)
        if self.config['include_logs']:
            self._backup_logs(backup_zip)
    
    def _backup_incremental(self, backup_zip):
        """Realiza backup incremental baseado no último backup"""
        logger.info("Executando backup incremental...")
        
        # Encontrar último backup completo
        ultimo_backup = self._encontrar_ultimo_backup_completo()
        
        if not ultimo_backup:
            logger.warning("Nenhum backup completo encontrado. Executando backup completo.")
            self._backup_completo(backup_zip)
            return
        
        # Obter timestamp do último backup
        ultimo_timestamp = self._obter_timestamp_backup(ultimo_backup)
        
        # Backup apenas de arquivos modificados
        self._backup_database(backup_zip)  # Sempre incluir DB atualizado
        self._backup_modified_files(backup_zip, ultimo_timestamp)
    
    def _backup_dados(self, backup_zip):
        """Backup apenas dos dados (banco de dados)"""
        logger.info("Executando backup de dados...")
        self._backup_database(backup_zip)
        self._backup_signatures(backup_zip)
    
    def _backup_configuracao(self, backup_zip):
        """Backup apenas das configurações"""
        logger.info("Executando backup de configurações...")
        self._backup_config_files(backup_zip)
        self._backup_python_files(backup_zip)
    
    def _backup_database(self, backup_zip):
        """Backup do banco de dados SQLite"""
        try:
            # Obter caminho do banco de dados
            db_path = self._get_database_path()
            
            if os.path.exists(db_path):
                # Criar backup do banco usando VACUUM INTO (SQLite 3.27+)
                temp_db_path = os.path.join(self.temp_dir, f'backup_db_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                
                try:
                    # Conectar ao banco original
                    conn = sqlite3.connect(db_path)
                    
                    # Fazer backup usando SQL
                    backup_conn = sqlite3.connect(temp_db_path)
                    conn.backup(backup_conn)
                    
                    conn.close()
                    backup_conn.close()
                    
                    # Adicionar ao ZIP
                    backup_zip.write(temp_db_path, 'database/ecocardiograma.db')
                    logger.info("Backup do banco de dados concluído")
                    
                finally:
                    # Limpar arquivo temporário
                    if os.path.exists(temp_db_path):
                        os.remove(temp_db_path)
            else:
                logger.warning(f"Banco de dados não encontrado: {db_path}")
                
        except Exception as e:
            logger.error(f"Erro no backup do banco de dados: {e}")
            raise
    
    def _backup_config_files(self, backup_zip):
        """Backup de arquivos de configuração"""
        config_files = [
            'app.py',
            'main.py',
            'routes.py',
            'models.py'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                backup_zip.write(config_file, f'config/{config_file}')
                logger.debug(f"Arquivo de configuração incluído: {config_file}")
    
    def _backup_templates_assets(self, backup_zip):
        """Backup de templates e assets"""
        directories = ['templates', 'static']
        
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = file_path.replace('\\', '/')
                        backup_zip.write(file_path, arcname)
                        logger.debug(f"Arquivo incluído: {file_path}")
    
    def _backup_python_files(self, backup_zip):
        """Backup de arquivos Python do utils"""
        utils_dir = 'utils'
        
        if os.path.exists(utils_dir):
            for root, dirs, files in os.walk(utils_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        arcname = file_path.replace('\\', '/')
                        backup_zip.write(file_path, arcname)
                        logger.debug(f"Arquivo Python incluído: {file_path}")
    
    def _backup_signatures(self, backup_zip):
        """Backup de assinaturas digitais"""
        # As assinaturas estão no banco de dados, mas podemos exportar separadamente
        try:
            from models import Medico
            from app import db
            
            signatures_data = []
            medicos = db.session.query(Medico).filter(Medico.assinatura_data.isnot(None)).all()
            
            for medico in medicos:
                signatures_data.append({
                    'id': medico.id,
                    'nome': medico.nome,
                    'crm': medico.crm,
                    'assinatura_data': medico.assinatura_data
                })
            
            if signatures_data:
                signatures_json = json.dumps(signatures_data, indent=2, ensure_ascii=False)
                backup_zip.writestr('signatures/assinaturas_digitais.json', signatures_json)
                logger.info(f"Backup de {len(signatures_data)} assinaturas digitais concluído")
                
        except Exception as e:
            logger.warning(f"Erro no backup de assinaturas: {e}")
    
    def _backup_generated_pdfs(self, backup_zip):
        """Backup de PDFs gerados"""
        pdf_dir = 'generated_pdfs'
        
        if os.path.exists(pdf_dir):
            for root, dirs, files in os.walk(pdf_dir):
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        arcname = f"pdfs/{file}"
                        backup_zip.write(file_path, arcname)
                        logger.debug(f"PDF incluído: {file_path}")
    
    def _backup_logs(self, backup_zip):
        """Backup de arquivos de log"""
        log_files = []
        
        # Procurar por arquivos de log comuns
        for pattern in ['*.log', 'logs/*.log', 'log/*.log']:
            import glob
            log_files.extend(glob.glob(pattern))
        
        for log_file in log_files:
            if os.path.exists(log_file):
                arcname = f"logs/{os.path.basename(log_file)}"
                backup_zip.write(log_file, arcname)
                logger.debug(f"Log incluído: {log_file}")
    
    def _backup_modified_files(self, backup_zip, since_timestamp):
        """Backup apenas de arquivos modificados desde o timestamp"""
        directories_to_check = ['templates', 'static', 'utils']
        
        for directory in directories_to_check:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_mtime = os.path.getmtime(file_path)
                        
                        if file_mtime > since_timestamp:
                            arcname = file_path.replace('\\', '/')
                            backup_zip.write(file_path, f"modified/{arcname}")
                            logger.debug(f"Arquivo modificado incluído: {file_path}")
    
    def _get_database_path(self):
        """Obtém o caminho do banco de dados"""
        # Tentar obter do app context se disponível
        if self.app:
            try:
                db_uri = self.app.config.get('SQLALCHEMY_DATABASE_URI', '')
                if db_uri.startswith('sqlite:///'):
                    return db_uri.replace('sqlite:///', '')
            except:
                pass
        
        # Fallback para arquivo padrão
        return 'ecocardiograma.db'
    
    def _verificar_integridade_backup(self, backup_path):
        """Verifica a integridade do arquivo de backup"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # Testar se o arquivo ZIP está íntegro
                bad_file = backup_zip.testzip()
                if bad_file:
                    logger.error(f"Arquivo corrompido no backup: {bad_file}")
                    return False
                
                # Verificar se contém metadados
                if 'backup_metadata.json' not in backup_zip.namelist():
                    logger.error("Metadados do backup não encontrados")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Erro na verificação de integridade: {e}")
            return False
    
    def _encontrar_ultimo_backup_completo(self):
        """Encontra o último backup completo"""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('backup_completo_') and filename.endswith('.zip'):
                filepath = os.path.join(self.backup_dir, filename)
                mtime = os.path.getmtime(filepath)
                backups.append((mtime, filepath))
        
        if backups:
            backups.sort(reverse=True)
            return backups[0][1]
        
        return None
    
    def _obter_timestamp_backup(self, backup_path):
        """Obtém o timestamp de criação de um backup"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                metadata_content = backup_zip.read('backup_metadata.json')
                metadata = json.loads(metadata_content)
                timestamp_str = metadata.get('timestamp')
                
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str).timestamp()
                    
        except Exception as e:
            logger.warning(f"Erro ao obter timestamp do backup: {e}")
        
        # Fallback para mtime do arquivo
        return os.path.getmtime(backup_path)
    
    def _limpar_backups_antigos(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        try:
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip'):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath)
                    backups.append((mtime, filepath, size))
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(reverse=True)
            
            # Remover backups excedentes
            if len(backups) > self.config['max_backups']:
                for _, backup_path, _ in backups[self.config['max_backups']:]:
                    os.remove(backup_path)
                    logger.info(f"Backup antigo removido: {backup_path}")
                    
        except Exception as e:
            logger.warning(f"Erro na limpeza de backups antigos: {e}")
    
    def restaurar_backup(self, backup_path, tipo_restauracao='COMPLETO'):
        """
        Restaura um backup
        
        Args:
            backup_path: Caminho do arquivo de backup
            tipo_restauracao: COMPLETO, DADOS, CONFIGURACAO
            
        Returns:
            bool: True se restauração foi bem-sucedida
        """
        try:
            logger.info(f"Iniciando restauração do backup: {backup_path}")
            
            # Verificar se o backup existe e é válido
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
            
            if not self._verificar_integridade_backup(backup_path):
                raise Exception("Backup corrompido ou inválido")
            
            # Criar backup de segurança antes da restauração
            backup_seguranca = self.criar_backup('COMPLETO', 'pre_restore_backup')
            logger.info(f"Backup de segurança criado: {backup_seguranca}")
            
            # Extrair e analisar metadados
            metadata = self._obter_metadata_backup(backup_path)
            logger.info(f"Restaurando backup do tipo: {metadata.get('tipo_backup', 'DESCONHECIDO')}")
            
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                if tipo_restauracao == 'COMPLETO':
                    self._restaurar_completo(backup_zip)
                elif tipo_restauracao == 'DADOS':
                    self._restaurar_dados(backup_zip)
                elif tipo_restauracao == 'CONFIGURACAO':
                    self._restaurar_configuracao(backup_zip)
                else:
                    raise ValueError(f"Tipo de restauração não suportado: {tipo_restauracao}")
            
            logger.info("Restauração concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na restauração: {str(e)}")
            raise
    
    def _obter_metadata_backup(self, backup_path):
        """Obtém metadados de um backup"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                metadata_content = backup_zip.read('backup_metadata.json')
                return json.loads(metadata_content)
        except Exception as e:
            logger.warning(f"Erro ao obter metadados: {e}")
            return {}
    
    def _restaurar_completo(self, backup_zip):
        """Restaura backup completo"""
        logger.info("Executando restauração completa...")
        
        # Restaurar banco de dados
        self._restaurar_database(backup_zip)
        
        # Restaurar arquivos de configuração
        self._restaurar_arquivos(backup_zip, 'config/', '')
        
        # Restaurar templates e assets
        self._restaurar_arquivos(backup_zip, 'templates/', 'templates/')
        self._restaurar_arquivos(backup_zip, 'static/', 'static/')
        
        # Restaurar utils
        self._restaurar_arquivos(backup_zip, 'utils/', 'utils/')
        
        # Restaurar assinaturas (se necessário)
        self._restaurar_assinaturas(backup_zip)
    
    def _restaurar_dados(self, backup_zip):
        """Restaura apenas dados"""
        logger.info("Executando restauração de dados...")
        self._restaurar_database(backup_zip)
        self._restaurar_assinaturas(backup_zip)
    
    def _restaurar_configuracao(self, backup_zip):
        """Restaura apenas configurações"""
        logger.info("Executando restauração de configurações...")
        self._restaurar_arquivos(backup_zip, 'config/', '')
        self._restaurar_arquivos(backup_zip, 'utils/', 'utils/')
    
    def _restaurar_database(self, backup_zip):
        """Restaura o banco de dados"""
        try:
            if 'database/ecocardiograma.db' in backup_zip.namelist():
                # Extrair banco de dados
                db_content = backup_zip.read('database/ecocardiograma.db')
                
                # Obter caminho de destino
                db_path = self._get_database_path()
                
                # Fazer backup do banco atual
                if os.path.exists(db_path):
                    backup_current_db = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(db_path, backup_current_db)
                    logger.info(f"Banco atual salvo como: {backup_current_db}")
                
                # Restaurar novo banco
                with open(db_path, 'wb') as db_file:
                    db_file.write(db_content)
                
                logger.info("Banco de dados restaurado com sucesso")
            else:
                logger.warning("Banco de dados não encontrado no backup")
                
        except Exception as e:
            logger.error(f"Erro na restauração do banco: {e}")
            raise
    
    def _restaurar_arquivos(self, backup_zip, source_prefix, dest_prefix):
        """Restaura arquivos de um diretório específico"""
        try:
            for file_info in backup_zip.infolist():
                if file_info.filename.startswith(source_prefix) and not file_info.is_dir():
                    # Calcular caminho de destino
                    relative_path = file_info.filename[len(source_prefix):]
                    dest_path = os.path.join(dest_prefix, relative_path)
                    
                    # Criar diretórios se necessário
                    dest_dir = os.path.dirname(dest_path)
                    if dest_dir:
                        os.makedirs(dest_dir, exist_ok=True)
                    
                    # Extrair arquivo
                    with backup_zip.open(file_info) as source:
                        with open(dest_path, 'wb') as dest:
                            dest.write(source.read())
                    
                    logger.debug(f"Arquivo restaurado: {dest_path}")
                    
        except Exception as e:
            logger.error(f"Erro na restauração de arquivos {source_prefix}: {e}")
            raise
    
    def _restaurar_assinaturas(self, backup_zip):
        """Restaura assinaturas digitais"""
        try:
            if 'signatures/assinaturas_digitais.json' in backup_zip.namelist():
                signatures_content = backup_zip.read('signatures/assinaturas_digitais.json')
                signatures_data = json.loads(signatures_content)
                
                logger.info(f"Restaurando {len(signatures_data)} assinaturas digitais")
                
                # Implementar restauração das assinaturas no banco de dados
                # (Isso requer acesso ao contexto da aplicação)
                
            else:
                logger.info("Nenhuma assinatura digital encontrada no backup")
                
        except Exception as e:
            logger.warning(f"Erro na restauração de assinaturas: {e}")
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip'):
                    filepath = os.path.join(self.backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    backup_info = {
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    }
                    
                    # Tentar obter metadados
                    try:
                        metadata = self._obter_metadata_backup(filepath)
                        backup_info.update({
                            'tipo': metadata.get('tipo_backup', 'DESCONHECIDO'),
                            'version': metadata.get('version', 'N/A'),
                            'sistema': metadata.get('sistema', 'N/A')
                        })
                    except:
                        backup_info.update({
                            'tipo': 'DESCONHECIDO',
                            'version': 'N/A',
                            'sistema': 'N/A'
                        })
                    
                    backups.append(backup_info)
            
            # Ordenar por data de criação (mais recente primeiro)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
        
        return backups
    
    def excluir_backup(self, backup_path):
        """Exclui um backup específico"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger.info(f"Backup excluído: {backup_path}")
                return True
            else:
                logger.warning(f"Backup não encontrado: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao excluir backup: {e}")
            raise
    
    def verificar_espaco_disco(self):
        """Verifica espaço disponível em disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.backup_dir)
            
            return {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': (used / total) * 100,
                'sufficient_space': free > (1024 * 1024 * 1024)  # 1GB mínimo
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar espaço em disco: {e}")
            return None
    
    def calcular_checksum(self, filepath):
        """Calcula checksum MD5 de um arquivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao calcular checksum: {e}")
            return None

# Funções de conveniência para uso externo
def criar_backup(tipo_backup='COMPLETO', nome_customizado=None):
    """Função de conveniência para criar backup"""
    manager = BackupManager()
    return manager.criar_backup(tipo_backup, nome_customizado)

def restaurar_backup(backup_path, tipo_restauracao='COMPLETO'):
    """Função de conveniência para restaurar backup"""
    manager = BackupManager()
    return manager.restaurar_backup(backup_path, tipo_restauracao)

def listar_backups_disponiveis():
    """Função de conveniência para listar backups"""
    manager = BackupManager()
    return manager.listar_backups()

def verificar_sistema_backup():
    """Verifica se o sistema de backup está funcionando corretamente"""
    try:
        manager = BackupManager()
        
        # Verificar diretório de backup
        if not os.path.exists(manager.backup_dir):
            return False, "Diretório de backup não existe"
        
        # Verificar espaço em disco
        espaco = manager.verificar_espaco_disco()
        if not espaco or not espaco['sufficient_space']:
            return False, "Espaço insuficiente em disco"
        
        # Verificar permissões de escrita
        test_file = os.path.join(manager.backup_dir, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except:
            return False, "Sem permissão de escrita no diretório de backup"
        
        return True, "Sistema de backup funcionando corretamente"
        
    except Exception as e:
        return False, f"Erro na verificação: {str(e)}"

# Configuração de backup automático (exemplo)
def configurar_backup_automatico(app):
    """Configura backup automático usando APScheduler (se disponível)"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler()
        
        # Backup diário às 2:00
        scheduler.add_job(
            func=lambda: criar_backup('COMPLETO'),
            trigger=CronTrigger(hour=2, minute=0),
            id='backup_diario',
            name='Backup Diário Automático',
            replace_existing=True
        )
        
        # Backup incremental a cada 4 horas
        scheduler.add_job(
            func=lambda: criar_backup('INCREMENTAL'),
            trigger=CronTrigger(hour='*/4'),
            id='backup_incremental',
            name='Backup Incremental Automático',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Backup automático configurado com sucesso")
        
        return scheduler
        
    except ImportError:
        logger.warning("APScheduler não disponível. Backup automático não configurado.")
        return None
    except Exception as e:
        logger.error(f"Erro ao configurar backup automático: {e}")
        return None
