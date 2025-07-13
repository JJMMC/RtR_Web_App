from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .articles import ArticuloResponse


# Schema para estadísticas de precios (nuevo)
class PriceStats(BaseModel):
    precio_actual: Optional[Decimal] = None
    precio_minimo: Optional[Decimal] = None
    precio_maximo: Optional[Decimal] = None
    precio_promedio: Optional[Decimal] = None
    total_registros: int = 0
    fecha_primer_precio: Optional[date] = None
    fecha_ultimo_precio: Optional[date] = None

# Schema para respuesta con estadísticas (nuevo)
class ArticuloWithStats(ArticuloResponse):
    estadisticas: Optional[PriceStats] = None
    model_config = ConfigDict(from_attributes=True)

# Schema para respuestas de operaciones (nuevo)
class OperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

