from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .hist_prices import HistorialPrecioResponse

# Schema base para Articulo
class ArticuloBase(BaseModel):
    rtr_id: int = Field(..., gt=0, description="ID único del producto en RTR")
    categoria: str = Field(..., min_length=1, max_length=100)
    nombre: str = Field(..., min_length=1, max_length=255)
    ean: Optional[int] = None
    art_url: Optional[str] = Field(None, max_length=500)
    img_url: Optional[str] = Field(None, max_length=500)

# Schema para crear artículos (puede incluir precio inicial)
class ArticuloCreate(ArticuloBase):
    precio_inicial: Optional[Decimal] = Field(None, ge=0, description="Precio inicial del producto")
    fecha_precio: Optional[date] = Field(None, description="Fecha del precio inicial")

# Schema para crear artículo CON precio inicial (más conveniente)
class ArticuloCreateWithPrice(ArticuloBase):
    precio_inicial: Decimal = Field(..., ge=0, description="Precio inicial obligatorio")
    fecha_precio: date = Field(default_factory=date.today, description="Fecha del precio inicial")

# Schema para actualizar artículos (nuevo)
class ArticuloUpdate(BaseModel):
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    ean: Optional[int] = None
    art_url: Optional[str] = Field(None, max_length=500)
    img_url: Optional[str] = Field(None, max_length=500)

# Schema para respuesta de Articulo (sin historial)
class ArticuloResponse(ArticuloBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Schema para la respuesta completa de artículo con historial
class ArticuloFullData(ArticuloResponse):
    historial_precios: List[HistorialPrecioResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

