from typing import List, Dict, Any, Tuple
from .crud_operations import articulo_crud, historial_crud
from .db_utils import scraped_to_dict, separate_article_and_price_data
#from scrap.scrap_url import scrap_rtr_crawler, scrap_rtr_crawler_by_cat
import logging

logger = logging.getLogger(__name__)

# Estas funciones mantienen la simplicidad de tu código actual
def insert_articulo(product_data: Dict[str, Any]) -> bool:
    """
    Insertar artículo - Compatible con tu función original
    Pero ahora usa la infraestructura mejorada
    """
    try:
        article_data, _ = separate_article_and_price_data(product_data)
        return articulo_crud.insert_one(article_data)
    except Exception as e:
        logger.error(f"Error inserting article: {e}")
        return False

def insert_precio(product_data: Dict[str, Any]) -> bool:
    """
    Insertar precio - Compatible con tu función original
    """
    try:
        _, price_data = separate_article_and_price_data(product_data)
        return historial_crud.insert_one(price_data)
    except Exception as e:
        logger.error(f"Error inserting price: {e}")
        return False

def articulo_already_in_table(product_data: Dict[str, Any]) -> bool:
    """
    Verificar si artículo existe - Misma funcionalidad que tu original
    """
    return articulo_crud.exists_by_rtr_id(product_data['rtr_id'])

def date_already_in_table(product_data: Dict[str, Any]) -> bool:
    """
    Verificar si fecha existe - Misma funcionalidad que tu original
    """
    return historial_crud.exists_for_date(product_data['rtr_id'], product_data['fecha'])

def insert_scraped(list_products: List[Tuple]) -> Dict[str, int]:
    """
    Función principal mejorada - Mantiene tu lógica original
    Ahora retorna estadísticas útiles
    """
    products_dict = scraped_to_dict(list_products)
    stats = {"articles_inserted": 0, "prices_inserted": 0, "skipped": 0}
    
    for product in products_dict:
        logger.info(f"Processing product: {product['nombre']}")
        
        # Tu lógica original, pero con mejor logging
        if not articulo_already_in_table(product):
            logger.info("Article not declared, inserting...")
            if insert_articulo(product):
                stats["articles_inserted"] += 1
                logger.info("Article inserted successfully")
            
            if insert_precio(product):
                stats["prices_inserted"] += 1
                logger.info("Price inserted successfully")
        else:
            logger.info("Article already declared, checking dates...")
            if not date_already_in_table(product):
                logger.info("New date found, inserting price...")
                if insert_precio(product):
                    stats["prices_inserted"] += 1
            else:
                logger.warning(f"Product already imported: {product['nombre']}")
                stats["skipped"] += 1
    
    return stats

def update_scraped() -> Dict[str, int]:
    """Tu función principal - Ahora con estadísticas"""
    logger.info("Starting scraped data update")
    scraped_data = scrap_rtr_crawler()
    stats = insert_scraped(scraped_data)
    logger.info(f"Update completed: {stats}")
    return stats

def update_scraped_by_cat(given_cat: str = 'Coches') -> Dict[str, int]:
    """Tu función por categoría - Ahora con estadísticas"""
    logger.info(f"Starting category update: {given_cat}")
    scraped_data = scrap_rtr_crawler_by_cat(given_cat)
    stats = insert_scraped(scraped_data)
    logger.info(f"Category update completed: {stats}")
    return stats

def first_insert_scraped_articulos() -> Dict[str, int]:
    """
    Primera inserción optimizada - Usa bulk insert para mejor rendimiento
    """
    logger.info("Starting first-time bulk insert")
    scraped_data = scrap_rtr_crawler()
    products_dict = scraped_to_dict(scraped_data)
    
    # Separar datos de artículos y precios
    articles_data = []
    prices_data = []
    
    for product in products_dict:
        article_data, price_data = separate_article_and_price_data(product)
        articles_data.append(article_data)
        prices_data.append(price_data)
    
    # Inserción masiva más eficiente
    articles_inserted = articulo_crud.bulk_insert(articles_data)
    prices_inserted = historial_crud.bulk_insert(prices_data)
    
    stats = {
        "articles_inserted": articles_inserted,
        "prices_inserted": prices_inserted,
        "skipped": 0
    }
    
    logger.info(f"First insert completed: {stats}")
    return stats