from orchestration.scraping_orchestrator import ScrapOrchestrator
from orchestration.data_orchestrator import DataOrchestrator
from database.crud_operations import articulo_crud, historial_crud
import logging
from schemas.articles import ArticuloCreate
from decimal import Decimal
from datetime import date


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
            # Validamos date para pylance
            valor = item[7]
            if isinstance(valor, str):
                fecha_precio = date.fromisoformat(valor)
            else:
                fecha_precio = valor                                                
            print(item[4])
            # # Creamos el artículo con Pydantic
            # articulo = ArticuloCreate(
            #         categoria=item[0],
            #         rtr_id= int(item[1]),
            #         nombre=item[2],
            #         precio_inicial= Decimal(item[3]),
            #         ean=int(item[4]),
            #         art_url=item[5],
            #         img_url=item[6],
            #         fecha_precio= fecha_precio
            #     )
            # print(articulo.nombre)

if __name__ == "__main__":
    test = MasterOrchestrator()
    test.run_complete_pipeline("Amortiguadores")