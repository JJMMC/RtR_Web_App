from scrap.schemas.schema_product import Product
from scrap.config.config import main_url
from scrap.web_navigation.web_tree import get_categories_tree
from scrap.utils.remove_duplicates import remove_duplicates_by_id
import logging
from scrap.engine.extractor import ProductsExtractor


class ScrapEngine:
    def __init__(self, logger=None, product_extractor=None):
        self.main_url = main_url
        self.logger = logger or self._create_default_logger()
        self.extractor = product_extractor or ProductsExtractor()
        self.stats = {'products_found': 0, 'errors': 0, 'categories_processed': 0}

    def _create_default_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger

    def scrap_category(self,cat, url):
        category_data_extrated = self.extractor.scrap_all_childs_in_cat(cat, url)
        return category_data_extrated
    
    def scrap_all_categories(self):
        # 1. Obtener categorías y URLs
        result = get_categories_tree()

        # 2. Iterar sobre cada categoría
        all_data = []
        for cat, url in result:
            # 3. Llamar a scrap_category() para cada una
            cat_data = self.scrap_category(cat,url)
            # 4. Aplanar resultados con .extend()
            all_data.extend(cat_data)
        # 5. Eliminar duplicados UNA VEZ al final
        all_data = remove_duplicates_by_id(all_data)
        # 6. Retornar lista plana
        return all_data