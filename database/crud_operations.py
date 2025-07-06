from typing import List, Dict, Any, Optional
from sqlalchemy import insert, select, and_
from .crud_base import CRUDOperations
from .db_models import Articulo, HistorialPrecio
from .db_session import db_manager
import logging

logger = logging.getLogger(__name__)

class ArticuloCRUD(CRUDOperations):
    """Operaciones CRUD específicas para artículos"""
    
    def insert_one(self, product_data: Dict[str, Any]) -> bool:
        """Insertar un artículo"""
        with self.get_session() as session:
            logger.info(f"Inserting article: {product_data.get('nombre', 'Unknown')}")
            session.execute(insert(Articulo), [product_data])
            session.commit()
            return True
    
    def bulk_insert(self, products_list: List[Dict[str, Any]]) -> int:
        """Insertar múltiples artículos de forma eficiente"""
        with self.get_session() as session:
            logger.info(f"Bulk inserting {len(products_list)} articles")
            session.execute(insert(Articulo), products_list)
            session.commit()
            return len(products_list)
    
    def exists_by_rtr_id(self, rtr_id: int) -> bool:
        """Verificar si existe artículo por RTR ID"""
        with self.get_session() as session:
            result = session.execute(
                select(Articulo.id).where(Articulo.rtr_id == rtr_id)
            ).scalar_one_or_none()
            return result is not None
    
    def get_by_id(self, id: int) -> Optional[Articulo]:
        """Obtener artículo por RTR ID"""
        with self.get_session() as session:
            return session.execute(
                select(Articulo).where(Articulo.id == id)
            ).scalar_one_or_none()
   
    def get_all(self):
        """
        Obtiene todos los artículos de la base de datos
        """
        with self.get_session() as session:
            if session is None:
                print('No hay Session')
        
            try:
                return session.query(Articulo).all()
            except Exception as e:
                print(f"Error al obtener todos los artículos: {e}")
                return []
            finally:
                if session:
                    session.close()

class HistorialCRUD(CRUDOperations):
    """Operaciones CRUD específicas para historial"""
    
    def insert_one(self, price_data: Dict[str, Any]) -> bool:
        """Insertar un precio"""
        with self.get_session() as session:
            logger.info(f"Inserting price for RTR_ID: {price_data.get('rtr_id')}")
            session.execute(insert(HistorialPrecio), [price_data])
            session.commit()
            return True
    
    def bulk_insert(self, prices_list: List[Dict[str, Any]]) -> int:
        """Insertar múltiples precios de forma eficiente"""
        with self.get_session() as session:
            logger.info(f"Bulk inserting {len(prices_list)} price records")
            session.execute(insert(HistorialPrecio), prices_list)
            session.commit()
            return len(prices_list)
    
    def exists_for_date(self, rtr_id: int, fecha: str) -> bool:
        """Verificar si existe precio para una fecha específica"""
        with self.get_session() as session:
            result = session.execute(
                select(HistorialPrecio.id).where(
                    and_(
                        HistorialPrecio.rtr_id == rtr_id,
                        HistorialPrecio.fecha == fecha
                    )
                )
            ).scalar_one_or_none()
            return result is not None
    
    def get_dates_by_rtr_id(self, rtr_id: int) -> List[str]:
        """Obtener todas las fechas registradas para un RTR ID"""
        with self.get_session() as session:
            results = session.execute(
                select(HistorialPrecio.fecha).where(HistorialPrecio.rtr_id == rtr_id)
            ).all()
            return [fecha[0] for fecha in results]

# Instancias globales para usar en funciones independientes
articulo_crud = ArticuloCRUD(db_manager)
historial_crud = HistorialCRUD(db_manager)

