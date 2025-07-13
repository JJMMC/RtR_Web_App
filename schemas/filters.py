from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal

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
