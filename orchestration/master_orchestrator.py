from orchestration.utils.pydantic_conversion import product_to_articlecreate, product_to_db_dict
from orchestration.scraping_orchestrator import ScrapOrchestrator
from orchestration.data_orchestrator import DataOrchestrator
from database.crud_operations import article_crud, price_record_crud, last_price_crud
import logging
from schemas.articles import ArticleCreate
from decimal import Decimal
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    def __init__(self):
        self.scrap_orch = ScrapOrchestrator()
        # No instanciamos DataOrchestrator xq se instancia cuando tienes datos a guardar/cargar
    
    def run_complete_pipeline(self, category: str|None = None):
        # 1. Scraping
        scraped_data = self.scrap_orch.run_category_scraping(category) if category else self.scrap_orch.run_full_scraping()
        if not scraped_data:
            logger.warning("No data scraped.")
            return print(f'Faliure during Scraping')
        
        # 2. Guardar temporal
        if not isinstance(scraped_data, list): # Validamos que es una lista antes de crear la instancia del objeto DataOrchestator
            logger.error("scraped_data no es una lista. No se puede guardar temporalmente.")
            return
        data_orch = DataOrchestrator(scraped_data)
        temp_file = data_orch.save_to_temp_file(prefix=category or "all")
        
        # 3. Insertar en base de datos usando CRUD directamente
        for item in scraped_data:
            try:
                article = product_to_articlecreate(item)
                article_dict = product_to_db_dict(item)
           
                if not article_crud.exists_by_rtr_id(article.rtr_id):
                    logger.info('New Article in DB')                   
                    article_crud.insert_one_with_price(article_dict)
                
                if price_record_crud.exists_for_date(article_dict['rtr_id'], article_dict['precio']):
                    logger.info('Price already updated')
                    continue

                data_to_update = {
                    "rtr_id" : article.rtr_id, 
                    "precio" : article.price,
                    "fecha" : article.record_date

                }
                price_record_crud.insert_one(data_to_update)
                last_price_crud.upsert_ultimo_precio(data_to_update['rtr_id'], data_to_update['precio'])
            except Exception as e:
                logger.warning(f"Invalid data structure skipped: {item}")
        
    def run_from_temp_file(self, file_path: str):
        data_orch = DataOrchestrator([])
        loaded = data_orch.load_from_temp_file(Path(file_path))
        if not loaded or "data" not in loaded:
            logger.error("No se pudieron cargar datos del archivo temporal.")
            return
        for item in loaded["data"]:
            try:
                article = product_to_articlecreate(item)
                article_dict = article.model_dump()
                if not article_crud.exists_by_rtr_id(article.rtr_id):
                    article_crud.insert_one(article_dict)
                article_crud.update_one(article.rtr_id, article_dict)
            except Exception as e:
                logger.warning(f"Invalid data structure skipped: {item} ({e})")

    def run_full_db_update(self):
        self.run_complete_pipeline(category=None)

    def validate_scraped_data(self, scraped_data):
        valid = 0
        invalid = 0
        for item in scraped_data:
            try:
                product_to_articlecreate(item)
                valid += 1
            except Exception:
                invalid += 1
        logger.info(f"Valid items: {valid}, Invalid items: {invalid}")


if __name__ == "__main__":
    test = MasterOrchestrator()
    test.run_complete_pipeline()

