from contextlib import contextmanager
# from typing import Optional, List
from sqlalchemy import create_engine, select, join
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from sqlalchemy.exc import SQLAlchemyError
from .db_models import Base, Article, PriceRecord
# from fastapi import HTTPException
# from schemas.articles import ArticuloFullData, ArticuloResponse
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Clase para manejar las operaciones de base de datos"""
    
    def __init__(self, database_url: str = 'sqlite:///rtr_crawler_Alchemy.db'):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Context manager para manejar sesiones de base de datos"""
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Crear todas las tablas en la base de datos"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise


# Instancia global del database manager
db_manager = DatabaseManager()

if __name__ == "__main__":
    #db_manager.create_tables()
    pass