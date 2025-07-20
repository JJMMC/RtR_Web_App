from scrap.engine.scraper import ScrapEngine
from scrap.web_navigation.web_tree import get_categories_tree
import requests
import time
import logging
from typing import Optional, Any


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ScrapOrchestrator:
    """
    Orquestador principal para gestionar el scraping de categorías y el scraping completo.
    Incluye lógica de reintentos y control de errores de red.
    """

    def __init__(self):
        # Dependency injection
        self.scrap_engine = ScrapEngine()
        

    def _retry_with_timeout(self, func, *args, **kwargs):
        """
        Ejecuta una función con lógica de reintentos ante timeout.
        
        Args:
            func (callable): Función a ejecutar.
            *args: Argumentos posicionales para la función.
            **kwargs: Argumentos nombrados para la función.
        
        Returns:
            Resultado de la función si tiene éxito, None si falla tras los reintentos.
        
        Raises:
            Propaga excepciones no relacionadas con timeout o errores de red.
        """
        count = 0
        while count < 5:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.Timeout:
                logger.warning("Timeout detectado. Esperando 5 segundos antes de reintentar...")
                time.sleep(5)
                count += 1
            except requests.RequestException as e:
                logger.error(f"Error en Request de red: {e}")
                break
            except Exception as e:
                logger.error(f"Error general: {e}")
                break
        return None 

    def run_full_scraping(self) -> Optional[dict[str, Any]]:
        """
        Ejecuta el scraping completo de todas las categorías con reintentos ante timeout.
        
        Returns:
            Resultado del scraping o None si falla tras los reintentos.
        """
        result = self._retry_with_timeout(self.scrap_engine.scrap_all_categories)
        return result
    
    def run_category_scraping(self, category: str) -> Optional[dict[str, Any]]:
        """
        Ejecuta el scraping de una categoría específica con reintentos ante timeout.
            
        Args:
            category (str): Nombre de la categoría a scrapear.
            
        Returns:
            Resultado del scraping o None si falla tras los reintentos.
            
        Raises:
            KeyError: Si la categoría no existe en el árbol de categorías.
        """

        url = dict(get_categories_tree())[category]
        result = self._retry_with_timeout(self.scrap_engine.scrap_category(category,url))
        return result
            
         
        
if __name__ == "__main__":
    scrap = ScrapOrchestrator()
    print(scrap.run_category_scraping('Coche'))

