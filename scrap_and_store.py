import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from database.sacrped_to_db import insert_scraped, update_scraped, update_scraped_by_cat
from scrap.scrap_data import scrap_data_from_web, scrap_all_childs_in_cat
from scrap.utils.remove_duplicates import remove_duplicates_by_id, get_duplicate_stats
import logging

logger = logging.getLogger(__name__)

TEMP_DIR = Path("temp_data")
TEMP_DIR.mkdir(exist_ok=True)

async def scrap_website(category: Optional[str] = None) -> List[Tuple]:
    """Scraper principal usando tu motor de scraping refactorizado"""
    try:
        if category:
            logger.info(f"Scraping category: {category}")
            # Necesitarías definir el mapping de categorías a URLs
            category_urls = {
                'Coches': 'https://www.rtrvalladolid.es/117-coches-crawler',
                # Agregar más categorías según necesites
            }
            
            if category in category_urls:
                cat_data = scrap_all_childs_in_cat(category, category_urls[category])
                return cat_data
            else:
                logger.warning(f"Category {category} not found, scraping all")
                return await scrap_all_categories()
        else:
            logger.info("Scraping all categories")
            return await scrap_all_categories()
            
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
        raise

async def scrap_all_categories() -> List[Tuple]:
    """Scrapea todas las categorías usando tu motor"""
    try:
        # Tu función scrap_data_from_web retorna una estructura anidada
        all_data = scrap_data_from_web()
        
        # Aplanar la estructura para obtener una lista de tuplas
        flattened_data = []
        for category_data in all_data:
            if isinstance(category_data, list):
                flattened_data.extend(category_data)
            else:
                flattened_data.append(category_data)
        
        # Eliminar duplicados usando tu función
        unique_data = remove_duplicates_by_id(flattened_data)
        
        logger.info(f"Scraped {len(unique_data)} unique products")
        return unique_data
        
    except Exception as e:
        logger.error(f"Error scraping all categories: {e}")
        raise

async def save_temp_data(data: List[Tuple], prefix: str = "scraped") -> Path:
    """Guarda datos temporalmente con estadísticas mejoradas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = TEMP_DIR / f"{prefix}_{timestamp}.json"
    
    # Obtener estadísticas antes de guardar
    stats = get_duplicate_stats(data)
    logger.info(f"Data stats: {stats}")
    
    # Convertir tuplas a formato serializable
    serializable_data = []
    for item in data:
        if len(item) >= 8:  # Validar estructura
            serializable_data.append({
                'categoria': item[0],
                'rtr_id': item[1], 
                'nombre': item[2],
                'precio': item[3],
                'ean': item[4],
                'art_url': item[5],
                'img_url': item[6],
                'fecha': str(item[7])  # Convertir fecha a string
            })
        else:
            logger.warning(f"Invalid data structure skipped: {item}")
    
    # Guardar datos y metadatos
    temp_data = {
        'timestamp': timestamp,
        'stats': stats,
        'data': serializable_data
    }
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(temp_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Data saved temporarily to: {temp_file}")
    logger.info(f"Total items saved: {len(serializable_data)}")
    return temp_file

def validate_scraped_data(data: List[Tuple]) -> List[Tuple]:
    """Valida y limpia los datos scrapeados usando tu lógica"""
    validated_data = []
    for item in data:
        if len(item) == 8 and item[1]:  # Verificar estructura y rtr_id
            validated_data.append(item)
        else:
            logger.warning(f"Invalid data item skipped: {item}")
    
    # Eliminar duplicados una vez más por seguridad
    final_data = remove_duplicates_by_id(validated_data)
    logger.info(f"Validation complete: {len(final_data)} valid items")
    
    return final_data

async def process_and_insert(data: List[Tuple]) -> Dict[str, int]:
    """
    Procesa e inserta usando tu lógica de 2 pasos:
    1. Si artículo existe -> insertar solo precio
    2. Si no existe -> crear artículo + insertar precio
    """
    try:
        # Validación y limpieza usando tus funciones
        validated_data = validate_scraped_data(data)
        
        if not validated_data:
            logger.warning("No valid data to process")
            return {"articles_inserted": 0, "prices_inserted": 0, "skipped": 0}
        
        # Inserción usando tu sistema existente que ya maneja la lógica de 2 pasos
        stats = insert_scraped(validated_data)
        logger.info(f"Database insertion completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise

async def scrape_and_store(category: Optional[str] = None, keep_temp: bool = False) -> Dict[str, int]:
    """Función principal orquestadora del proceso completo"""
    try:
        logger.info("=== STARTING SCRAPE AND STORE PROCESS ===")
        
        # 1. SCRAPING FASE
        logger.info("Phase 1: Scraping data...")
        scraped_data = await scrap_website(category=category)
        
        if not scraped_data:
            logger.warning("No data scraped")
            return {"articles_inserted": 0, "prices_inserted": 0, "skipped": 0}
        
        # 2. TEMPORARY STORAGE FASE
        logger.info("Phase 2: Saving temporary data...")
        temp_file = await save_temp_data(
            scraped_data, 
            prefix=f"scraped_{category}" if category else "scraped_all"
        )
        
        # 3. DATABASE INSERTION FASE
        logger.info("Phase 3: Processing and inserting to database...")
        stats = await process_and_insert(scraped_data)
        
        # 4. CLEANUP FASE
        logger.info("Phase 4: Cleanup...")
        if stats.get("articles_inserted", 0) > 0 or stats.get("prices_inserted", 0) > 0:
            if not keep_temp:
                temp_file.unlink()
                logger.info("✅ Process completed successfully, temporary file deleted")
            else:
                logger.info(f"✅ Process completed successfully, temporary file preserved: {temp_file}")
        else:
            logger.warning(f"⚠️ No data inserted, temporary file preserved: {temp_file}")
        
        logger.info(f"=== PROCESS COMPLETED: {stats} ===")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error in scrape_and_store: {e}")
        return {"articles_inserted": 0, "prices_inserted": 0, "skipped": 0}


# Función para listar archivos temporales disponibles
def list_temp_files() -> List[Dict[str, Any]]:
    """Lista archivos temporales disponibles para recuperación"""
    temp_files = []
    for file_path in TEMP_DIR.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            file_info = {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'created': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # Agregar estadísticas si están disponibles
            if isinstance(data, dict) and 'stats' in data:
                file_info['stats'] = data['stats']
                file_info['items_count'] = len(data.get('data', []))
            else:
                file_info['items_count'] = len(data) if isinstance(data, list) else 0
            
            temp_files.append(file_info)
            
        except Exception as e:
            logger.warning(f"Could not read temp file {file_path}: {e}")
    
    return sorted(temp_files, key=lambda x: x['created'], reverse=True)

# Uso recomendado:
# await scrape_and_store()  # Scrapea todo
# await scrape_and_store(category="Coches")  # Solo coches  
# await quick_update()  # Usa tu función existente
# await recover_from_temp("temp_data/scraped_20240101_120000.json")
# list_temp_files()  # Ver archivos disponibles