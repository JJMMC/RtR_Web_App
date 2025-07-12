from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy import insert, select, and_, update
from .crud_base import CRUDOperations
from .db_models import Articulo, HistorialPrecio
from .db_session import db_manager
import logging
import schemas

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
    
    def update_one(self, article_id, updated_data: Dict[str, Any]):
        with self.get_session() as session:
            logger.info(f"Inserting article: {updated_data.get('nombre', 'Unknown')}")
            # 1.- Verificar si existe
            existing = session.execute(
                select(Articulo).where(Articulo.id == article_id)
            ).scalar_one_or_none()

            if not existing:
                raise Exception(f"Article with id {article_id} not found")

            # 2.- Luego actualizar
            session.execute(
                update(Articulo)
                .where(Articulo.id == article_id)
                .values(updated_data)
            )

            # 3. COMMIT los cambios
            session.commit()
            
            # 4. Obtener y retornar el objeto actualizado
            updated_article = session.execute(
                select(Articulo).where(Articulo.id == article_id)
            ).scalar_one()
            return updated_article    
           
    def exists_by_rtr_id(self, rtr_id: int) -> bool:
        """Verificar si existe artículo por RTR ID"""
        with self.get_session() as session:
            result = session.execute(
                select(Articulo.id).where(Articulo.rtr_id == rtr_id)
            ).scalar_one_or_none()
            return result is not None
    
    def get_by_id(self, id: int) -> Optional[Articulo]:
        """Obtener artículo por ID"""
        with self.get_session() as session:
            return session.execute(
                select(Articulo).where(Articulo.id == id)
            ).scalar_one_or_none()
    
    def get_by_rtr_id(self, rtr_id: int) -> Optional[Articulo]:
        """Obtener artículo por RTR ID"""
        with self.get_session() as session:
            return session.execute(
                select(Articulo).where(Articulo.rtr_id == rtr_id)
            ).scalar_one_or_none()
   
    def get_all(self) -> List[Articulo]:
        """Obtener todos los artículos"""
        with self.get_session() as session:
            try:
                return session.query(Articulo).all()
            except Exception as e:
                logger.error(f"Error getting all articles: {e}")
                raise  # Propagar el error para que la capa API lo maneje
        # Context manager se encarga del cierre automáticamente

    def search(self, filters: Dict[str, Any], limit: int = 20) -> Sequence[Articulo]:
        with self.get_session() as session:
            
            
            # Lista para acumular condiciones
            article_conditions = []
            pricedate_conditions = []


            if 'nombre' in filters:
                article_conditions.append(Articulo.nombre.ilike(f"%{filters['nombre']}%"))
            
            if 'categoria' in filters:
                article_conditions.append(Articulo.categoria.ilike(f"%{filters['categoria']}%"))
            
            if 'rtr_id' in filters:
                article_conditions.append(Articulo.rtr_id == filters['rtr_id'])
            
            if 'ean' in filters:
                article_conditions.append(Articulo.ean == filters['ean'])
            
            if 'max_price' in filters:
                pricedate_conditions.append(HistorialPrecio.precio <= filters['max_price'])

            if 'min_price' in filters:
                pricedate_conditions.append(HistorialPrecio.precio >= filters['min_price'])

            if 'max_date' in filters:
                pricedate_conditions.append(HistorialPrecio.fecha <= filters['max_date'])

            if 'min_date' in filters:
                pricedate_conditions.append(HistorialPrecio.fecha >= filters['min_date'])


            # Creamos el Query, Si no hay filtros de precio/fecha, evitar JOIN
            if not pricedate_conditions:
                query = select(Articulo)  
                if article_conditions:
                    query = query.where(and_(*article_conditions))
            else:
                # Creamos el query en funcíon de las condiciones junto con las de precio y fecha
                query = select(Articulo).join(HistorialPrecio, HistorialPrecio.rtr_id == Articulo.rtr_id).distinct()
                
                # Aplicar TODAS las condiciones con AND
                all_conditions = article_conditions + pricedate_conditions
                if all_conditions:
                    query = query.where(and_(*all_conditions))
                
            query = query.limit(limit)
            return session.execute(query).scalars().all()

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

