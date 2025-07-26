from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal


# Schema base para PriceRecord (SIN rtr_id redundante)
class PriceRecordBase(BaseModel):
    price: Decimal = Field(..., ge=0, description="Precio debe ser mayor o igual a 0")
    record_date: date

# Schema para respuesta de PriceRecord (SIN rtr_id redundante)
class PriceRecordResponse(PriceRecordBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Schema para crear precios (requiere que el artículo ya exista)
class PriceRecordCreate(BaseModel):
    price: Decimal = Field(..., ge=0, description="Precio del producto")
    record_date: date = Field(default_factory=date.today, description="Fecha del precio")
    
    # Nota: rtr_id se tomará del artículo al que se asocia el precio