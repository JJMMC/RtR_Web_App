from contextlib import contextmanager
from typing import List, Dict, Any
from sqlalchemy import insert, select
from .db_session import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class CRUDOperations:
    """Clase base para operaciones CRUD con manejo centralizado de sesiones"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    @contextmanager
    def get_session(self):
        """Wrapper del context manager para logging adicional"""
        with self.db_manager.get_session() as session:
            logger.debug("Database session started")
            try:
                yield session
            except Exception as e:
                logger.error(f"Database operation failed: {e}")
                raise
            finally:
                logger.debug("Database session closed")

                