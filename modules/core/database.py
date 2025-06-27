"""
Gerenciador de Banco de Dados

Módulo centralizado para operações de banco de dados,
proporcionando interface segura e padronizada.
"""

from typing import Any, Dict, List, Optional, Type
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app import db
from .exceptions import DatabaseError

class DatabaseManager:
    """Gerenciador centralizado de operações de banco de dados"""
    
    @staticmethod
    def save_entity(entity: db.Model) -> db.Model:
        """Salva entidade no banco de dados"""
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro ao salvar entidade: {str(e)}", "SAVE")
    
    @staticmethod
    def update_entity(entity: db.Model) -> db.Model:
        """Atualiza entidade no banco de dados"""
        try:
            db.session.merge(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro ao atualizar entidade: {str(e)}", "UPDATE")
    
    @staticmethod
    def delete_entity(entity: db.Model) -> bool:
        """Remove entidade do banco de dados"""
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro ao deletar entidade: {str(e)}", "DELETE")
    
    @staticmethod
    def get_by_id(model_class: Type[db.Model], entity_id: int) -> Optional[db.Model]:
        """Busca entidade por ID"""
        try:
            return db.session.get(model_class, entity_id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar entidade por ID: {str(e)}", "GET_BY_ID")
    
    @staticmethod
    def get_all(model_class: Type[db.Model], order_by: str = None, limit: int = None) -> List[db.Model]:
        """Busca todas as entidades de um modelo"""
        try:
            query = db.session.query(model_class)
            
            if order_by:
                if hasattr(model_class, order_by):
                    query = query.order_by(getattr(model_class, order_by).desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar entidades: {str(e)}", "GET_ALL")
    
    @staticmethod
    def search_by_field(model_class: Type[db.Model], field_name: str, value: Any) -> List[db.Model]:
        """Busca entidades por campo específico"""
        try:
            if hasattr(model_class, field_name):
                field = getattr(model_class, field_name)
                return db.session.query(model_class).filter(field.ilike(f"%{value}%")).all()
            else:
                raise DatabaseError(f"Campo '{field_name}' não existe no modelo", "SEARCH")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar por campo: {str(e)}", "SEARCH")
    
    @staticmethod
    def execute_query(query_func, *args, **kwargs) -> Any:
        """Executa query personalizada com tratamento de erro"""
        try:
            return query_func(*args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro ao executar query: {str(e)}", "CUSTOM_QUERY")
    
    @staticmethod
    def get_statistics() -> Dict[str, int]:
        """Obtém estatísticas gerais do banco"""
        try:
            from models import Exame, ParametrosEcocardiograma, Medico
            
            stats = {
                'total_exames': db.session.query(Exame).count(),
                'exames_hoje': db.session.query(Exame).filter(
                    Exame.data_exame == db.func.current_date()
                ).count(),
                'total_medicos': db.session.query(Medico).filter(Medico.ativo == True).count(),
                'parametros_preenchidos': db.session.query(ParametrosEcocardiograma).count()
            }
            
            return stats
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao obter estatísticas: {str(e)}", "STATISTICS")
    
    @staticmethod
    def bulk_insert(entities: List[db.Model]) -> bool:
        """Insere múltiplas entidades em lote"""
        try:
            db.session.add_all(entities)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro ao inserir em lote: {str(e)}", "BULK_INSERT")
    
    @staticmethod
    def transaction(operations: List[callable]) -> bool:
        """Executa múltiplas operações em uma transação"""
        try:
            for operation in operations:
                operation()
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise DatabaseError(f"Erro na transação: {str(e)}", "TRANSACTION")