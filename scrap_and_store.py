import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from database.sacrped_to_db import insert_scraped, update_scraped, update_scraped_by_cat
from scrap.scrap_url import scrap_rtr_crawler, scrap_rtr_crawler_by_cat
import logging

logger = logging.getLogger(__name__)

TEMP_DIR = Path("temp_data")
TEMP_DIR.mkdir(exist_ok=True)

async def scrape_website(url: str = None, category: str = None) -> List[Tuple]:
    """Scraper principal que usa tu lógica existente"""
    try:
        if category:
            logger.info(f"Scraping category: {category}")
            return scrap_rtr_crawler_by_cat(category)
        else:
            logger.info("Scraping all categories")
            return scrap_rtr_crawler()
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
        raise

async def save_temp_data(data: List[Tuple], prefix: str = "scraped") -> Path:
    """Guarda datos temporalmente y retorna la ruta del archivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = TEMP_DIR / f"{prefix}_{timestamp}.json"
    
    # Convertir tuplas a formato serializable
    serializable_data = []
    for item in data:
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
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Data saved temporarily to: {temp_file}")
    return temp_file

def validate_scraped_data(data: List[Tuple]) -> List[Tuple]:
    """Valida y limpia los datos scrapeados"""
    # Aquí puedes agregar validaciones específicas
    # Por ahora retorna los datos tal como están
    validated_data = []
    for item in data:
        if len(item) == 8 and item[1]:  # Verificar que tenga rtr_id
            validated_data.append(item)
        else:
            logger.warning(f"Invalid data item skipped: {item}")
    
    return validated_data

async def process_and_insert(data: List[Tuple]) -> Dict[str, int]:
    """Procesa y almacena en BD usando tu sistema existente"""
    try:
        # Validación y limpieza
        validated_data = validate_scraped_data(data)
        
        # Inserción usando tu función existente
        stats = insert_scraped(validated_data)
        logger.info(f"Database insertion completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise

async def scrape_and_store(category: str = None, keep_temp: bool = False) -> Dict[str, int]:
    """Función principal que orquesta todo el proceso"""
    try:
        # 1. Scraping
        scraped_data = await scrape_website(category=category)
        
        # 2. Guardar temporalmente
        temp_file = await save_temp_data(scraped_data, 
                                       prefix=f"scraped_{category}" if category else "scraped_all")
        
        # 3. Procesar e insertar
        stats = await process_and_insert(scraped_data)
        
        # 4. Limpiar archivo temporal si es exitoso y no se quiere mantener
        if stats["articles_inserted"] > 0 or stats["prices_inserted"] > 0:
            if not keep_temp:
                temp_file.unlink()
                logger.info("Process completed, temporary file deleted")
            else:
                logger.info(f"Process completed, temporary file preserved: {temp_file}")
        else:
            logger.warning(f"No data inserted, temporary file preserved: {temp_file}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error in scrape_and_store: {e}")
        return {"articles_inserted": 0, "prices_inserted": 0, "skipped": 0, "error": str(e)}

# Funciones de conveniencia que usan tu API existente
async def quick_update() -> Dict[str, int]:
    """Actualización rápida usando tu función update_scraped"""
    try:
        stats = update_scraped()
        logger.info(f"Quick update completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error in quick update: {e}")
        return {"error": str(e)}

async def update_by_category(category: str = 'Coches') -> Dict[str, int]:
    """Actualización por categoría usando tu función existente"""
    try:
        stats = update_scraped_by_cat(category)
        logger.info(f"Category update completed: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error in category update: {e}")
        return {"error": str(e)}

# Función para recuperar datos de archivos temporales
async def recover_from_temp(temp_file_path: str) -> Dict[str, int]:
    """Recuperar e insertar datos desde un archivo temporal"""
    try:
        temp_file = Path(temp_file_path)
        if not temp_file.exists():
            raise FileNotFoundError(f"Temporary file not found: {temp_file_path}")
        
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convertir de vuelta a tuplas para usar con tu sistema
        tuple_data = []
        for item in data:
            tuple_data.append((
                item['categoria'],
                item['rtr_id'],
                item['nombre'],
                item['precio'],
                item['ean'],
                item['art_url'],
                item['img_url'],
                item['fecha']
            ))
        
        stats = await process_and_insert(tuple_data)
        logger.info(f"Recovery completed: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error recovering from temp file: {e}")
        return {"error": str(e)}

# Uso directo:
# await scrape_and_store()  # Scrapea todo
# await scrape_and_store(category="Coches")  # Solo coches
# await quick_update()  # Usa tu función existente
# await recover_from_temp("temp_data/scraped_20240101_120000.json")