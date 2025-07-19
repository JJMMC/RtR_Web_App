
from scrap.web_navigation.web_tree import get_categories_tree
import requests
import time
import logging

class DataOrchestrator:
    def __init__(self, scraped_data):
        # Dependency injection
        self.scraped_data = scraped_data

    def _retry_with_timeout(self, func, *args, **kwargs):

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

    def run_full_scraping(self):
        """
        Ejecuta el scraping completo de todas las categorías con reintentos ante timeout.
        
        Returns:
            Resultado del scraping o None si falla tras los reintentos.
        """
        result = self._retry_with_timeout(self.scrap_engine.scrap_all_categories)
        return result
    
    def run_category_scraping(self, category):
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
