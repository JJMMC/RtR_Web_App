from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal


# Schema base para HistorialPrecio (SIN rtr_id redundante)
class HistorialPrecioBase(BaseModel):
    precio: Decimal = Field(..., ge=0, description="Precio debe ser mayor o igual a 0")
    fecha: date

# Schema para respuesta de HistorialPrecio (SIN rtr_id redundante)
class HistorialPrecioResponse(HistorialPrecioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Schema para crear precios (requiere que el artículo ya exista)
class HistorialPrecioCreate(BaseModel):
    precio: Decimal = Field(..., ge=0, description="Precio del producto")
    fecha: date = Field(default_factory=date.today, description="Fecha del precio")
    
    # Nota: rtr_id se tomará del artículo al que se asocia el precio

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


# Schema para filtros de búsqueda
class ArticuloFilter(BaseModel):
    id: Optional[str] = None
    rtr_id: Optional[str] = None
    ean: Optional[str] = None
    categoria: Optional[str] = None
    nombre: Optional[str] = None
    precio_min: Optional[Decimal] = None
    precio_max: Optional[Decimal] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None

# # Schema para estadísticas de precios (nuevo)
# class PriceStats(BaseModel):
#     precio_actual: Optional[Decimal] = None
#     precio_minimo: Optional[Decimal] = None
#     precio_maximo: Optional[Decimal] = None
#     precio_promedio: Optional[Decimal] = None
#     total_registros: int = 0
#     fecha_primer_precio: Optional[date] = None
#     fecha_ultimo_precio: Optional[date] = None

# # Schema para respuesta con estadísticas (nuevo)
# class ArticuloWithStats(ArticuloResponse):
#     estadisticas: Optional[PriceStats] = None
#     model_config = ConfigDict(from_attributes=True)

# # Schema para respuestas de operaciones (nuevo)
# class OperationResponse(BaseModel):
#     success: bool
#     message: str
#     data: Optional[dict] = None