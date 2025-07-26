from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .articles import ArticleResponse


# Schema RESPONSE para estadísticas de precios (nuevo)
class PriceStats(BaseModel):
    actual_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    avg_price: Optional[Decimal] = None
    total_records: int = 0
    first_price_date: Optional[date] = None
    last_price_date: Optional[date] = None



# Schema para Stats básicos de todas las categorías
class CategoryStatsResponse(BaseModel):
    category: str                    # Nombre de la categoría
    total_products: int             # Cuántos productos tiene
    avg_price: Decimal         # Precio medio de productos en la categoría
    min_price: Decimal           # Producto más barato
    max_price: Decimal           # Producto más caro
    last_update: date       # Última vez que se actualizó algún precio



# Schema para respuesta con estadísticas (nuevo)
class ArticleWithStats(ArticleResponse):
    statistics: Optional[PriceStats] = None
    model_config = ConfigDict(from_attributes=True)

# Schema para respuestas de operaciones (nuevo)
class OperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

