from typing import List, Dict, Any, Optional, Sequence
from sqlalchemy import insert, select, and_, update, func
from sqlalchemy.orm import joinedload 
from .crud_base import CRUDOperations
from .db_models import Article, PriceRecord, LastPrice
from .db_session import db_manager
from datetime import date
from decimal import Decimal
import logging
# from schemas.articles import ArticleCreate

logger = logging.getLogger(__name__)

class ArticleCRUD(CRUDOperations): # Clase para trabajar con la tabla Artículos de la DB
    """Operaciones CRUD Básicas para artículos"""
    
    def insert_one(self, product_data: Dict[str, Any]) -> bool:
        """Insertar un artículo"""
        with self.get_session() as session:
            logger.info(f"Inserting article: {product_data.get('name', 'Unknown')}")
            new_article = Article(**product_data) 
            session.add(new_article)
            session.commit()
            return True
    
    # función cuando insertamos el artíuclo por primera vez, con precio    
    def insert_one_with_price(self, product_data: Dict[str, Any]) -> bool:
        """Insertar un artículo y su precio en historial y último precio"""
        with self.get_session() as session:
            try:
                # 1. Insertar artículo
                logger.info(f"Inserting article: {product_data.get('name', 'Unknown')}")
                new_article = Article(
                    rtr_id=product_data["rtr_id"],
                    category=product_data["category"],
                    name=product_data["name"],
                    ean=product_data.get("ean"),
                    art_url=product_data.get("art_url"),
                    img_url=product_data.get("img_url"),
                )
                session.add(new_article)
                session.flush()  # Para obtener el id si lo necesitas

                # 2. Insertar historial de precios
                historial = PriceRecord(
                    rtr_id=product_data["rtr_id"],
                    price=product_data["price"],
                    record_date=product_data["record_date"],
                )
                session.add(historial)

                # 3. Insertar/actualizar último precio
                existing = session.execute(
                    select(LastPrice).where(LastPrice.rtr_id == product_data["rtr_id"])
                ).scalar_one_or_none()
                if existing is None:
                    ultimo = LastPrice(
                        rtr_id=product_data["rtr_id"],
                        price=product_data["price"],
                        record_date=product_data["record_date"],
                    )
                    session.add(ultimo)
                else:
                    existing.price = product_data["price"]
                    existing.record_date = product_data["record_date"]

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
            session.execute(insert(Article), products_list)
            session.commit()
            return len(products_list)
    
    def update_one(self, rtr_id, updated_data: Dict[str, Any]):
        with self.get_session() as session:
            logger.info(f"Inserting article: {updated_data.get('name', 'Unknown')}")
            # 1.- Verificar si existe
            existing = session.execute(
                select(Article).where(Article.rtr_id == rtr_id)
            ).scalar_one_or_none()

            if not existing:
                raise Exception(f"Article with id {rtr_id} not found")

            # 2.- Luego actualizar
            session.execute(
                update(Article)
                .where(Article.rtr_id == rtr_id)
                .values(updated_data)
            )

            # 3. COMMIT los cambios
            session.commit()
            
            # 4. Obtener y retornar el objeto actualizado
            updated_article = session.execute(
                select(Article).where(Article.rtr_id == rtr_id)
            ).scalar_one()
            return updated_article    
           
    def exists_by_rtr_id(self, rtr_id: int) -> bool:
        """Verificar si existe artículo por RTR ID"""
        with self.get_session() as session:
            result = session.execute(
                select(Article.id).where(Article.rtr_id == rtr_id)
            ).scalar_one_or_none()
            return result is not None
    
    def get_by_id(self, id: int) -> Optional[Article]:
        """Obtener artículo por ID"""
        with self.get_session() as session:
            return session.execute(
                select(Article).where(Article.id == id)
            ).scalar_one_or_none()
    
    def get_by_rtr_id(self, rtr_id: int) -> Optional[Article]:
        """Obtener artículo por RTR ID"""
        with self.get_session() as session:
            return session.execute(
                select(Article).where(Article.rtr_id == rtr_id)
            ).scalar_one_or_none()
   
    def get_all(self) -> List[Article]:
        """Obtener todos los artículos"""
        with self.get_session() as session:
            try:
                return session.query(Article).all()
            except Exception as e:
                logger.error(f"Error getting all articles: {e}")
                raise  # Propagar el error para que la capa API lo maneje
        # Context manager se encarga del cierre automáticamente

    def search(self, filters: Dict[str, Any], limit: int = 20) -> Sequence[Article]:
        with self.get_session() as session:
            
            
            # Lista para acumular condiciones
            article_conditions = []


            if 'name' in filters:
                article_conditions.append(Article.name.ilike(f"%{filters['name']}%"))
            
            if 'category' in filters:
                article_conditions.append(Article.category.ilike(f"%{filters['category']}%"))
            
            if 'rtr_id' in filters:
                article_conditions.append(Article.rtr_id == filters['rtr_id'])
            
            if 'ean' in filters:
                article_conditions.append(Article.ean == filters['ean'])

            # Creamos el Query
            query = select(Article)  
            query = query.where(and_(*article_conditions))    
            query = query.limit(limit)

            return session.execute(query).scalars().all()

    def search_with_history(self, filters: Dict[str, Any], limit: int = 20) -> Sequence[Article]:
        with self.get_session() as session:
            
            
            # Lista para acumular condiciones
            article_conditions = []
            pricedate_conditions = []


            if 'name' in filters:
                article_conditions.append(Article.name.ilike(f"%{filters['name']}%"))
            
            if 'category' in filters:
                article_conditions.append(Article.category.ilike(f"%{filters['category']}%"))
            
            if 'rtr_id' in filters:
                article_conditions.append(Article.rtr_id == filters['rtr_id'])
            
            if 'ean' in filters:
                article_conditions.append(Article.ean == filters['ean'])
            
            if 'max_price' in filters:
                pricedate_conditions.append(PriceRecord.price <= filters['max_price'])

            if 'min_price' in filters:
                pricedate_conditions.append(PriceRecord.price >= filters['min_price'])

            if 'max_date' in filters:
                pricedate_conditions.append(PriceRecord.record_date <= filters['max_date'])

            if 'min_date' in filters:
                pricedate_conditions.append(PriceRecord.record_date >= filters['min_date'])




            # Como el endpoint ya valida que existen filtros de precio/fecha,
            # siempre necesitaremos JOIN y eager loading
            query = (select(Article)
                    .options(joinedload(Article.price_records))
                    .join(PriceRecord, PriceRecord.rtr_id == Article.rtr_id)
                    .distinct())
                
            # Aplicar TODAS las condiciones con AND
            all_conditions = article_conditions + pricedate_conditions
            query = query.where(and_(*all_conditions))    
            query = query.limit(limit)

            return session.execute(query).scalars().unique().all()
        
    def get_all_categories(self):
        with self.get_session() as session:
            return session.execute(select(Article.category).distinct().where(Article.category.is_not(None))).scalars().all()


class PriceRecordCRUD(CRUDOperations): # Clase para trabajar con la tabla Historial-precios de la DB
    """Operaciones CRUD específicas para historial"""
    
    def insert_one(self, price_data: Dict[str, Any]) -> bool:
        """Insertar un precio"""
        with self.get_session() as session:
            logger.info(f"Inserting price for RTR_ID: {price_data.get('rtr_id')}")
            session.execute(insert(PriceRecord), [price_data])
            session.commit()
            return True


    def bulk_insert(self, prices_list: List[Dict[str, Any]]) -> int:
        """Insertar múltiples precios de forma eficiente"""
        with self.get_session() as session:
            logger.info(f"Bulk inserting {len(prices_list)} price records")
            session.execute(insert(PriceRecord), prices_list)
            session.commit()
            return len(prices_list)
    
    def exists_for_date(self, rtr_id: int, record_date: str) -> bool:
        """Verificar si existe precio para una fecha específica"""
        with self.get_session() as session:
            result = session.execute(
                select(PriceRecord.id).where(
                    and_(
                        PriceRecord.rtr_id == rtr_id,
                        PriceRecord.record_date == record_date
                    )
                )
            ).scalar_one_or_none()
            return result is not None
    
    def get_dates_by_rtr_id(self, rtr_id: int) -> List[str]:
        """Obtener todas las fechas registradas para un RTR ID"""
        with self.get_session() as session:
            results = session.execute(
                select(PriceRecord.record_date).where(PriceRecord.rtr_id == rtr_id)
            ).all()
            return [fecha[0] for fecha in results]


class LastPriceCRUD(CRUDOperations): # Clase para trabajar con la tabla ultimo precio de la DB
    """Operaciones CRUD específicas para Ultimo Precio"""

    def get_by_rtr_id(self, rtr_id: int)-> Optional[LastPrice]:
        with self.get_session() as session:
            query = (select(LastPrice).where(LastPrice.rtr_id == rtr_id))
            return session.execute(query).scalar()
    
    def upsert_ultimo_precio(self, rtr_id: int, price: Decimal):
        with self.get_session() as session:
            record_date = date.today()
            existing = session.execute(select(LastPrice).where(LastPrice.rtr_id == rtr_id)).scalar_one_or_none()
            
            # En caso de que el artículo NO esté creado
            if existing is None:
                # NO EXISTE → CREATE (INSERT)
                logger.info(f"Creando nuevo último price para RTR_ID: {rtr_id}")
                new_price = LastPrice(rtr_id=rtr_id, price=price, record_date=record_date)
                session.add(new_price)

            # En caso de que el artículo SÍ esté creado
            else:
                # SÍ EXISTE → UPDATE
                logger.info(f"Actualizando último precio para RTR_ID: {rtr_id}")
                existing.price = price
                existing.record_date = record_date
            
            # Guardamos los Cambios
            session.commit()

            
class AnalyticsCRUD(CRUDOperations):
    """Operaciones específicas para analytics y estadísticas"""
    
    def get_all_categories_stats(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            query = (
                select(
                    Article.category, # CAMPO 1: La categoría (por la que vamos a agrupar)
                    func.count(func.distinct(Article.id)).label('total_products'), # AGREGACIÓN 1: Contar cuántos productos hay por categoría
                    func.avg(PriceRecord.price).label('avg_price'), # AGREGACIÓN 2: Calcular el precio promedio por categoría
                    func.min(PriceRecord.price).label('min_price'), # AGREGACIÓN 3: Encontrar el precio MÁS BARATO por categoría
                    func.max(PriceRecord.price).label('max_price'), # AGREGACIÓN 4: Encontrar el precio MÁS CARO por categoría
                    func.max(PriceRecord.record_date).label('last_update') # AGREGACIÓN 5: Encontrar la última fecha de esa categoría
                )
                .join(PriceRecord, Article.rtr_id == PriceRecord.rtr_id) # UNIR LAS TABLAS: Conectar artículos con sus últimos precios
                .group_by(Article.category) # GROUP BY: Agrupar por categoría Con esto obtenemos UNA fila POR CADA categoría
            )
            
            results = session.execute(query).all()
            stats = []
            for row in results:
                stats.append({
                    'category': row.category,
                    'total_products': row.total_products,
                    'avg_price': row.avg_price,
                    'min_price': row.min_price,
                    'max_price': row.max_price,
                    'last_update': row.last_update
                })
            
            return stats

    def get_category_stats(self, given_category) -> Dict[str, Any]:
        with self.get_session() as session:
            query = (
                select(
                    Article.category,
                    func.count(func.distinct(Article.id)).label('total_products'),
                    func.avg(PriceRecord.price).label('avg_price'),
                    func.min(PriceRecord.price).label('min_price'),
                    func.max(PriceRecord.price).label('max_price'),
                    func.max(PriceRecord.record_date).label('last_update')
                )
                .join(PriceRecord, Article.rtr_id == PriceRecord.rtr_id)
                .where(Article.category == given_category)
                .group_by(Article.category)  
            )
            
            result = session.execute(query).first()  
            
            if not result:
                return {}
                
            return {
                'category': result.category,
                'total_products': result.total_products,
                'avg_price': result.avg_price,
                'min_price': result.min_price,
                'max_price': result.max_price,
                'last_update': result.last_update
            }


class UserCRUD(CRUDOperations):
    pass




# Instancias globales para usar en funciones independientes
article_crud = ArticleCRUD(db_manager)
price_record_crud = PriceRecordCRUD(db_manager)
analytics_crud = AnalyticsCRUD(db_manager)
last_price_crud = LastPriceCRUD(db_manager)
user_crud = UserCRUD(db_manager)