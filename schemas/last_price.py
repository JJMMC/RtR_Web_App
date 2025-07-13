from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from decimal import Decimal
from .hist_prices import HistorialPrecioResponse

class UltimoPrecioBase(BaseModel):
    rtr_id: int
    precio: Decimal
    fecha: date

class UltimoPrecioCreate(UltimoPrecioBase):
    pass

class UltimoPrecioResponse(UltimoPrecioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)