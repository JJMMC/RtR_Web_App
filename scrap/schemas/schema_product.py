from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
import re

class Product(BaseModel):
    """Modelo Pydantic para representar un producto scrapeado"""
    
    category: str
    rtr_id: str
    name: str
    price: str
    ean: Optional[str]
    url: str
    image_url: str
    scraped_date: date
    
    @field_validator('price')
    @classmethod
    def format_price(cls, v):
        """Formatea el precio eliminando € y ajustando decimales"""
        if hasattr(v, 'text'):
            # Si viene de BeautifulSoup
            price = v.text.replace("€", "").replace(",", ".").strip()
        else:
            # Si ya es string
            price = str(v).replace("€", "").replace(",", ".").strip()
            
        # Si tiene más de 6 caracteres, quitar el primer punto
        if len(price) > 6:
            price = price.replace(".", "", 1)
        return price
    
    @field_validator('name')
    @classmethod
    def format_name(cls, v):
        """Limpia y formatea el nombre básico"""
        if isinstance(v, str):
            return v.strip()
        return str(v).strip()
    
    @model_validator(mode='after')
    def correct_incomplete_name(self):
        """Corrige nombres incompletos usando información de la URL"""
        if '...' in self.name and self.url:
            # Extraer nombre desde URL
            url_name = self._extract_name_from_url(self.url)
            if url_name:
                self.name = self._fix_incomplete_name(self.name, url_name)
                
        return self
    
    @staticmethod
    def _extract_name_from_url(url: str) -> Optional[str]:
        """Extrae el nombre del producto desde la URL"""
        pattern = r"(-\d+[\w-]+)\.html"
        match = re.search(pattern, url)
        if not match:
            return None
            
        full_match = match.group(1)
        
        # Buscar el nombre del item
        pattern = r"-\d+([a-zA-Z0-9-]+)-\d+$"
        item_match = re.search(pattern, full_match)
        if item_match:
            item_name = item_match.group(1)
        else:
            pattern = r"-\d+([a-zA-Z0-9-]+)"
            item_match = re.search(pattern, full_match)
            if item_match:
                item_name = item_match.group(1)
            else:
                return None
                
        # Formatear nombre
        item_name = item_name.replace("-", " ").capitalize()
        return item_name
    
    @staticmethod
    def _fix_incomplete_name(incomplete_name: str, url_name: str) -> str:
        """Corrige nombres incompletos añadiendo texto faltante"""
        incomplete_name = incomplete_name.replace('...', '').strip()
        incomplete_words = incomplete_name.replace('/', '').lower().split()
        missing_words = ''
        
        for word in url_name.lower().split():
            if word not in incomplete_words:
                missing_words = f'{missing_words} {word.capitalize()}'
        
        return incomplete_name + missing_words
    
    @classmethod
    def from_url(cls, url: str, category: str, name: str, price, 
                 image_url: str, scraped_date: date | None):
        """Factory method para crear Product desde URL y datos scrapeados"""
        
        # Extraer información de la URL
        rtr_id, ean = cls._extract_url_info(url)
        
        if scraped_date is None:
            scraped_date = datetime.now().date()
            
        return cls(
            category=category,
            rtr_id=rtr_id,
            name=name,
            price=price,
            ean=ean,
            url=url,
            image_url=image_url,
            scraped_date=scraped_date
        )
    
    @staticmethod
    def _extract_url_info(url: str) -> tuple[str, Optional[str]]:
        """Extrae RTR ID y EAN desde la URL"""
        pattern = r"(-\d+[\w-]+)\.html"
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f"No se pudo extraer información de la URL: {url}")
            
        full_match = match.group(1)
        
        # RTR ID
        pattern = r"^-(\d+)"
        rtr_id_match = re.search(pattern, full_match)
        if not rtr_id_match:
            raise ValueError(f"No se pudo extraer RTR ID de: {full_match}")
        rtr_id = rtr_id_match.group(1)
        
        # EAN (opcional)
        pattern = r"-(\d+)$"
        ean_match = re.search(pattern, full_match)
        ean = ean_match.group(1) if ean_match else None
        
        return rtr_id, ean
    
    def to_tuple(self) -> tuple:
        """Convierte el producto a tupla para compatibilidad con código existente"""
        return (
            self.category,
            self.rtr_id,
            self.name,
            self.price,
            self.ean,
            self.url,
            self.image_url,
            self.scraped_date
        )
    
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True
    }