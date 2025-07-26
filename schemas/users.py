from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal
from .hist_prices import PriceRecordResponse
from .last_price import LastPriceResponse
from datetime import datetime

# Schema base para Usuarios
class UserBase(BaseModel):    
    user_name: str = Field(..., min_length=1, max_length=255)
    name : Optional[str] = Field(None, min_length=1, max_length=255)
    surname: Optional[str] = Field(None, min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=100)
    
    is_active: bool = Field(default=False)
    role: str = Field(..., min_length=1, max_length=255)
    
class UserCreate(UserBase):   
    password: str = Field(..., min_length=1, max_length=100)

class UserLogin(BaseModel):
    email: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)

class UserResponse(UserBase):
    created_at: datetime


