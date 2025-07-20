import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
import logging
from schemas.articles import ArticuloCreate
from decimal import Decimal
from datetime import date

logger = logging.getLogger(__name__)

TEMP_DIR = Path("temp_data")
TEMP_DIR.mkdir(exist_ok=True)

class DataOrchestrator:
    def __init__(self, scraped_data: List[Tuple]):
        # Dependency injection
        self.scraped_data = scraped_data

    def save_to_temp_file(self, prefix: str = "scraped") -> Path:
        """
        Guarda datos scrapeados a un archivo JSON temporal.
        
        Args:
            prefix: Para componer el nombre del archivo
        
        Returns:
            Ruta del archivo creado.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = TEMP_DIR / f"{prefix}_{timestamp}.json"
        
        # Convertir tuplas a formato serializable
        serializable_data = []
        for item in self.scraped_data:
            try:
                articulo = ArticuloCreate(
                    categoria=item[0],
                    rtr_id=item[1],
                    nombre=item[2],
                    precio_inicial=item[3],
                    ean=item[4],
                    art_url=item[5],
                    img_url=item[6],
                    fecha_precio=item[7]
                )
                data = articulo.model_dump()
                if isinstance(data.get("precio_inicial"), Decimal):
                    data["precio_inicial"] = float(data["precio_inicial"])
                if isinstance(data.get('fecha_precio'), date):
                    data['fecha_precio'] = str(data['fecha_precio'])
                serializable_data.append(data)
            except Exception as e:
                logger.warning(f"Invalid data structure skipped: {item}")
        
        # Guardar datos y metadatos
        temp_data = {
        'timestamp': timestamp,
        'data': serializable_data
        }

        with open(temp_file, 'w', encoding='utf-8') as file:
            json.dump(temp_data, file, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved temporarily to: {temp_file}")
        logger.info(f"Total items saved: {len(serializable_data)}")

        
        return temp_file
    
    def load_from_temp_file(self, file_path: Path) -> Optional[dict]:
        """
        Carga datos scrapeados desde un archivo JSON temporal.
        
        Args:
            file_path (Path): Ruta al archivo JSON a cargar.
        
        Returns:
            dict con los datos cargados, o None si hay error.
        """
        if not file_path.exists():
            logger.error(f"El archivo {file_path} no existe.")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Datos cargados correctamente desde: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error al cargar datos de {file_path}: {e}")
            return None

    def delete_temp_file(self, file_path: Path) -> bool:
        """
        Elimina el archivo JSON temporal.
        
        Args:
            file_path (Path): Ruta al archivo JSON a eliminar.
        
        Returns:
            True = Exito | False= algo fallo.
        """
        if not file_path.exists():
            logger.error(f"El archivo {file_path} no existe.")
            return False
        
        try:
            file_path.unlink()
            logger.info(f"Archivo eliminado: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"El archivo {file_path} no se pudo borrar.")
            return False
        
    def list_temp_files(self) -> List[Dict[str, Any]]:
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
                
                # # Agregar estadísticas si están disponibles
                # if isinstance(data, dict) and 'stats' in data:
                #     file_info['stats'] = data['stats']
                #     file_info['items_count'] = len(data.get('data', []))
                # else:
                #     file_info['items_count'] = len(data) if isinstance(data, list) else 0
                
                # temp_files.append(file_info)
                
            except Exception as e:
                logger.warning(f"Could not read temp file {file_path}: {e}")
        
        return sorted(temp_files, key=lambda x: x['created'], reverse=True)



if __name__ == "__main__":
    pass
