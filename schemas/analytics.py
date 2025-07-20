from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .articles import ArticleResponse


# Schema RESPONSE para estadísticas de precios (nuevo)
class PriceStats(BaseModel):
    precio_actual: Optional[Decimal] = None
    precio_minimo: Optional[Decimal] = None
    precio_maximo: Optional[Decimal] = None
    precio_promedio: Optional[Decimal] = None
    total_registros: int = 0
    fecha_primer_precio: Optional[date] = None
    fecha_ultimo_precio: Optional[date] = None



# Schema para Stats básicos de todas las categorías
class CategoriaStatsResponse(BaseModel):
    categoria: str                    # Nombre de la categoría
    total_productos: int             # Cuántos productos tiene
    precio_promedio: Decimal         # Precio medio de productos en la categoría
    precio_minimo: Decimal           # Producto más barato
    precio_maximo: Decimal           # Producto más caro
    ultima_actualizacion: date       # Última vez que se actualizó algún precio



# Schema para respuesta con estadísticas (nuevo)
class ArticuloWithStats(ArticleResponse):
    estadisticas: Optional[PriceStats] = None
    model_config = ConfigDict(from_attributes=True)

# Schema para respuestas de operaciones (nuevo)
class OperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

