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
class Articulo(Base):
    __tablename__ = "articulos"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    rtr_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True )  # Clave primaria correctamente definida
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    ean: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    art_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    img_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relación con historial_precios
    historial: Mapped[list["HistorialPrecio"]] = relationship(back_populates="articulo")
    
    # Relación con ultimo_precio
    precio_actualizado: Mapped["UltimoPrecio"] = relationship(back_populates="articulo", uselist=False)

# Definir la tabla de historial de precios
class HistorialPrecio(Base):
    __tablename__ = "historial_precios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rtr_id: Mapped[int] = mapped_column(Integer, ForeignKey("articulos.rtr_id"), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 10 dígitos con 2 decimales
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relación con Articulos
    articulo: Mapped["Articulo"] = relationship(back_populates="historial")
    
# Definir la tabla de ultimo precio
class UltimoPrecio(Base):
    __tablename__ = "ultimo_precio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rtr_id: Mapped[int] = mapped_column(Integer, ForeignKey("articulos.rtr_id"), nullable=False, unique=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # 10 dígitos con 2 decimales
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relación con Articulos
    articulo: Mapped["Articulo"] = relationship(back_populates="precio_actualizado")





