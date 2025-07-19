from scrap.schemas.schema_product import Product
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from scrap.utils.config import main_url
from scrap.engine.soup_gen import soup_generator
from pydantic import ValidationError
from itertools import zip_longest
from scrap.web_navigation.scrap_cat_urls import request_categorias_and_main_urls, find_child_urls
from scrap.utils.remove_duplicates import remove_duplicates_by_id
import logging


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
        result = request_categorias_and_main_urls()

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


class ProductsExtractor:
    # def __init__(self):
    #     self.main_url = main_url
    
    def extract_safe_data(self, soup, selector, attr_chain=None):
        """Extrae datos de forma segura con verificación de tipos"""
        elements = soup.find_all(*selector) if isinstance(selector, tuple) else soup.find_all(selector)
        results = []
        
        for element in elements:
            if isinstance(element, Tag):
                if attr_chain:
                    # Para casos como img.get('data-full-size-image-url')
                    value = element
                    for step in attr_chain:
                        if callable(step):
                            value = step(value)
                        else:
                            value = getattr(value, step, None)
                        if not value:
                            break
                    if value:
                        results.append(value)
                else:
                    # Para casos simples como .string
                    if element.string:
                        results.append(element.string)
        
        return results
    
    def scrap_product_details_in_child(self, url, cat):    
        print(f"\nObteniendo información: Categoria:{cat} {url}")

        # Generamos la sopa para la url child
        child_soup = soup_generator(url)
        if not child_soup:
            return []
            

        # EXTRACCIÓN REFACTORIZADA - Más limpia y menos propensa a errores
        prod_urls = self.extract_safe_data(
            child_soup, 
            ('div', {'class': 'product-description'}),
            [lambda div: div.find('a'), lambda a: a.get('href') if a else None]
        )
        
        prod_names = self.extract_safe_data(child_soup, 'h2')
        
        prod_prices = self.extract_safe_data(child_soup, ('span', {'class': 'price'}))
        
        prod_image_urls = self.extract_safe_data(
            child_soup,
            ('a', {'class': 'thumbnail'}),
            [lambda a: a.find('img'), lambda img: img.get('data-full-size-image-url') if img else None]
        )

        # CREAR PRODUCTOS CON PYDANTIC
        # Utilizamos pydantic para que valide, formatee y extraiga la info que falta.
        # La magia aquí la hace Pydantic 
        products = []
        fecha = datetime.now().date()
        
        # zip_longest maneja listas de diferentes tamaños automáticamente
        for href, name, price, image_url in zip_longest(
            prod_urls, prod_names, prod_prices, prod_image_urls,
            fillvalue=""):
            if not href:  # Skip si no hay URL
                continue
                
            try:
                product = Product.from_url(
                    url=href,
                    category=cat,
                    name=name or "Producto sin nombre",
                    price=price or "0€",
                    image_url=image_url or "",
                    scraped_date=fecha
                )
                products.append(product)
                
            except Exception as e:
                print(f"⚠️  Error procesando producto {href}: {e}")
                continue
                
        
        # Resultado, lista de productos que aparecen en una url child:
            # - Validados
            # - Corregidos / reformateados
            # - Retornados en forma de tuplas
        # CONVERTIR A TUPLAS PARA COMPATIBILIDAD
        return [product.to_tuple() for product in products]
    
    def scrap_all_childs_in_cat(self, cat, main_cat_url):
        cat_data = []
        child_urls = find_child_urls(main_cat_url)
        for url in child_urls:
            child_url_data = self.scrap_product_details_in_child(url,cat)
            cat_data.extend(child_url_data)
        cat_data = remove_duplicates_by_id(cat_data)
        return cat_data