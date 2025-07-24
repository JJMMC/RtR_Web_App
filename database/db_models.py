from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Date, func, String, Integer, Numeric
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from typing import Optional
from decimal import Decimal
from datetime import date



# Configurar la base de datos en memoria
#engine = create_engine('sqlite:///database/rtr_crawler_Alchemy.db')#echo=True echo=true para depuración de código


# Definir la base declarativa
class Base(DeclarativeBase):
    pass

# Definir la tabla de artículos
class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    rtr_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True )  # Clave primaria correctamente definida
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ean: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    art_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    img_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relación con price_record
    price_records: Mapped[list["PriceRecord"]] = relationship(back_populates="article")
    
    # Relación con last_price
    updated_price: Mapped["LastPrice"] = relationship(back_populates="article", uselist=False)

# Definir la tabla de historial de precios
class PriceRecord(Base):
    __tablename__ = "price_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rtr_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.rtr_id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 10 dígitos con 2 decimales
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relación con Articles
    article: Mapped["Article"] = relationship(back_populates="price_records")
    
# Definir la tabla de ultimo precio
class LastPrice(Base):
    __tablename__ = "last_price"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rtr_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.rtr_id"), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 10 dígitos con 2 decimales
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relación con Articles
    article: Mapped["Article"] = relationship(back_populates="updated_price")





