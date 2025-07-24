from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .hist_prices import PriceRecordResponse
from .last_price import LastPriceResponse

# Schema base para Articulo
class ArticleBase(BaseModel):
    rtr_id: int = Field(..., gt=0, description="ID único del producto en RTR")
    category: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    ean: Optional[int] = None
    art_url: Optional[str] = Field(None, max_length=500)
    img_url: Optional[str] = Field(None, max_length=500)

# Schema para crear artículos (puede incluir precio inicial)
class ArticleCreateOptionalPrice(ArticleBase):
    price: Optional[Decimal] = Field(None, ge=0, description="Precio inicial del producto")
    price_date: Optional[date] = Field(None, description="Fecha del precio inicial")

# Schema para crear artículo CON precio inicial (más conveniente)
class ArticleCreate(ArticleBase):
    price: Decimal = Field(..., ge=0, description="Precio inicial obligatorio")
    price_date: date = Field(default_factory=date.today, description="Fecha del precio inicial")

# Schema para actualizar artículos (nuevo)
class ArticleUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ean: Optional[int] = None
    art_url: Optional[str] = Field(None, max_length=500)
    img_url: Optional[str] = Field(None, max_length=500)

# Schema para respuesta de Articulo (sin historial)
class ArticleResponse(ArticleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Schema para la respuesta completa de artículo con historial
class ArticleFullData(ArticleResponse):
    price_history: List[PriceRecordResponse] = Field(default_factory=list)
    updated_price: Optional[LastPriceResponse]
    
    model_config = ConfigDict(from_attributes=True)

