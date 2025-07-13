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