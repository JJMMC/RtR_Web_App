from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from decimal import Decimal
from .hist_prices import PriceRecordResponse

class LastPriceBase(BaseModel):
    rtr_id: int
    precio: Decimal
    fecha: date

class LastPriceCreate(LastPriceBase):
    pass

class LastPriceResponse(LastPriceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)