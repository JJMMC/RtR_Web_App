from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy import insert, select, and_, update, func
from sqlalchemy.orm import joinedload 
from .crud_base import CRUDOperations
from .db_models import Articulo, HistorialPrecio, UltimoPrecio
from .db_session import db_manager
from datetime import date
from decimal import Decimal
import logging
from schemas.articles import ArticleCreate

logger = logging.getLogger(__name__)

class ArticuloCRUD(CRUDOperations): # Clase para trabajar con la tabla Artículos de la DB
    """Operaciones CRUD Básicas para artículos"""
    
    def insert_one(self, product_data: Dict[str, Any]) -> bool:
        """Insertar un artículo"""
        with self.get_session() as session:
            logger.info(f"Inserting article: {product_data.get('name', 'Unknown')}")
            new_article = Articulo(**product_data) 
            session.add(new_article)
            session.commit()
            return True
    
    # función cuando insertamos el artíuclo por primera vez, con precio    
    def insert_one_with_price(self, product_data: Dict[str, Any]) -> bool:
        """Insertar un artículo y su precio en historial y último precio"""
        with self.get_session() as session:
            try:
                # 1. Insertar artículo
                logger.info(f"Inserting article: {product_data.get('nombre', 'Unknown')}")
                new_article = Articulo(
                    rtr_id=product_data["rtr_id"],
                    categoria=product_data["categoria"],
                    nombre=product_data["nombre"],
                    ean=product_data.get("ean"),
                    art_url=product_data.get("art_url"),
                    img_url=product_data.get("img_url"),
                )
                session.add(new_article)
                session.flush()  # Para obtener el id si lo necesitas

                # 2. Insertar historial de precios
                historial = HistorialPrecio(
                    rtr_id=product_data["rtr_id"],
                    precio=product_data["precio"],
                    fecha=product_data["fecha"],
                )
                session.add(historial)

                # 3. Insertar/actualizar último precio
                existing = session.execute(
                    select(UltimoPrecio).where(UltimoPrecio.rtr_id == product_data["rtr_id"])
                ).scalar_one_or_none()
                if existing is None:
                    ultimo = UltimoPrecio(
                        rtr_id=product_data["rtr_id"],
                        precio=product_data["precio"],
                        fecha=product_data["fecha"],
                    )
                    session.add(ultimo)
                else:
                    existing.precio = product_data["precio"]
                    existing.fecha = product_data["fecha"]

                session.commit()
                return True
            except Exception as e:
                logger.error(f"Error inserting article with price: {e}")
                session.rollback()
                return False
    
    def bulk_insert(self, products_list: List[Dict[str, Any]]) -> int:
        """Insertar múltiples artículos de forma eficiente"""
        with self.get_session() as session:
            logger.info(f"Bulk inserting {len(products_list)} articles")
            session.execute(insert(Articulo), products_list)
            session.commit()
            return len(products_list)
    
    def update_one(self, rtr_id, updated_data: Dict[str, Any]):
        with self.get_session() as session:
            logger.info(f"Inserting article: {updated_data.get('nombre', 'Unknown')}")
            # 1.- Verificar si existe
            existing = session.execute(
                select(Articulo).where(Articulo.rtr_id == rtr_id)
            ).scalar_one_or_none()

            if not existing:
                raise Exception(f"Article with id {rtr_id} not found")

            # 2.- Luego actualizar
            session.execute(
                update(Articulo)
                .where(Articulo.rtr_id == rtr_id)
                .values(updated_data)
            )

            # 3. COMMIT los cambios
            session.commit()
            
            # 4. Obtener y retornar el objeto actualizado
            updated_article = session.execute(
                select(Articulo).where(Articulo.rtr_id == rtr_id)
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


            if 'nombre' in filters:
                article_conditions.append(Articulo.nombre.ilike(f"%{filters['nombre']}%"))
            
            if 'categoria' in filters:
                article_conditions.append(Articulo.categoria.ilike(f"%{filters['categoria']}%"))
            
            if 'rtr_id' in filters:
                article_conditions.append(Articulo.rtr_id == filters['rtr_id'])
            
            if 'ean' in filters:
                article_conditions.append(Articulo.ean == filters['ean'])

            # Creamos el Query
            query = select(Articulo)  
            query = query.where(and_(*article_conditions))    
            query = query.limit(limit)

            return session.execute(query).scalars().all()

    def search_with_history(self, filters: Dict[str, Any], limit: int = 20) -> Sequence[Articulo]:
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




            # Como el endpoint ya valida que existen filtros de precio/fecha,
            # siempre necesitaremos JOIN y eager loading
            query = (select(Articulo)
                    .options(joinedload(Articulo.historial))
                    .join(HistorialPrecio, HistorialPrecio.rtr_id == Articulo.rtr_id)
                    .distinct())
                
            # Aplicar TODAS las condiciones con AND
            all_conditions = article_conditions + pricedate_conditions
            query = query.where(and_(*all_conditions))    
            query = query.limit(limit)

            return session.execute(query).scalars().unique().all()
        
    def get_all_categories(self):
        with self.get_session() as session:
            return session.execute(select(Articulo.categoria).distinct().where(Articulo.categoria.is_not(None))).scalars().all()


class HistorialCRUD(CRUDOperations): # Clase para trabajar con la tabla Historial-precios de la DB
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


class UltimoPrecioCRUD(CRUDOperations): # Clase para trabajar con la tabla ultimo precio de la DB
    """Operaciones CRUD específicas para Ultimo Precio"""

    def get_by_rtr_id(self, rtr_id: int)-> Optional[UltimoPrecio]:
        with self.get_session() as session:
            query = (select(UltimoPrecio).where(UltimoPrecio.rtr_id == rtr_id))
            return session.execute(query).scalar()
    
    def upsert_ultimo_precio(self, rtr_id: int, precio: Decimal):
        with self.get_session() as session:
            fecha = date.today()
            existing = session.execute(select(UltimoPrecio).where(UltimoPrecio.rtr_id == rtr_id)).scalar_one_or_none()
            
            # En caso de que el artículo NO esté creado
            if existing is None:
                # NO EXISTE → CREATE (INSERT)
                logger.info(f"Creando nuevo último precio para RTR_ID: {rtr_id}")
                new_price = UltimoPrecio(rtr_id=rtr_id, precio=precio, fecha=fecha)
                session.add(new_price)

            # En caso de que el artículo SÍ esté creado
            else:
                # SÍ EXISTE → UPDATE
                logger.info(f"Actualizando último precio para RTR_ID: {rtr_id}")
                existing.precio = precio
                existing.fecha = fecha
            
            # Guardamos los Cambios
            session.commit()

            
class AnalyticsCRUD(CRUDOperations):
    """Operaciones específicas para analytics y estadísticas"""
    
    def get_all_categories_stats(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            query = (
                select(
                    Articulo.categoria, # CAMPO 1: La categoría (por la que vamos a agrupar)
                    func.count(Articulo.id).label('total_productos'), # AGREGACIÓN 1: Contar cuántos productos hay por categoría
                    func.avg(UltimoPrecio.precio).label('precio_promedio'), # AGREGACIÓN 2: Calcular el precio promedio por categoría
                    func.min(UltimoPrecio.precio).label('precio_minimo'), # AGREGACIÓN 3: Encontrar el precio MÁS BARATO por categoría
                    func.max(UltimoPrecio.precio).label('precio_maximo'), # AGREGACIÓN 4: Encontrar el precio MÁS CARO por categoría
                    func.max(UltimoPrecio.fecha).label('fecha_ultimo_precio') # AGREGACIÓN 5: Encontrar la última fecha de esa categoría
                )
                .join(UltimoPrecio, Articulo.rtr_id == UltimoPrecio.rtr_id) # UNIR LAS TABLAS: Conectar artículos con sus últimos precios
                .group_by(Articulo.categoria) # GROUP BY: Agrupar por categoría Con esto obtenemos UNA fila POR CADA categoría
            )
            
            results = session.execute(query).all()
            
            # Convertir a lista de diccionarios
            stats = []
            for row in results:
                stats.append({
                    'categoria': row.categoria,
                    'total_productos': row.total_productos,
                    'precio_promedio': row.precio_promedio,
                    'precio_minimo': row.precio_minimo,
                    'precio_maximo': row.precio_maximo,
                    'ultima_actualizacion': row.fecha_ultimo_precio
                })
            
            return stats

    def get_category_stats(self, category) -> Dict[str, Any]:
        with self.get_session() as session:
            query = (
                select(
                    Articulo.categoria,
                    func.count(Articulo.id).label('total_productos'),
                    func.avg(UltimoPrecio.precio).label('precio_promedio'),
                    func.min(UltimoPrecio.precio).label('precio_minimo'),
                    func.max(UltimoPrecio.precio).label('precio_maximo'),
                    func.max(UltimoPrecio.fecha).label('fecha_ultimo_precio')
                )
                .join(UltimoPrecio, Articulo.rtr_id == UltimoPrecio.rtr_id)
                .where(Articulo.categoria == category)
                .group_by(Articulo.categoria)  
            )
            
            result = session.execute(query).first()  
            
            if not result:
                return {}
                
            return {
                'categoria': result.categoria,
                'total_productos': result.total_productos,
                'precio_promedio': result.precio_promedio,
                'precio_minimo': result.precio_minimo,
                'precio_maximo': result.precio_maximo,
                'ultima_actualizacion': result.fecha_ultimo_precio
            }       







# Instancias globales para usar en funciones independientes
articulo_crud = ArticuloCRUD(db_manager)
historial_crud = HistorialCRUD(db_manager)
analytics_crud = AnalyticsCRUD(db_manager)
ultimo_precio_crud = UltimoPrecioCRUD(db_manager)
