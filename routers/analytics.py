from fastapi import APIRouter, HTTPException, Query
import schemas.analytics
from typing import List
from datetime import date
from decimal import Decimal
from database.crud_operations import article_crud, analytics_crud
from database.db_session import db_manager
from database.db_models import Article
from sqlalchemy import select



router = APIRouter(
    prefix="/analytics",      # prefijo común para estas rutas
    tags=["Analytics"]        # agrupación en la documentación
)


#### ANALITYCS STATS

@router.get("/categories", response_model=List[schemas.analytics.CategoryStatsResponse])
def get_categories_stats():
    categories_stats = analytics_crud.get_all_categories_stats()
    if not categories_stats:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # categories_stats = []
    # for category in categories:
    #     categories_stats.append(analytics_crud.get_all_categories_stats())
    return categories_stats


@router.get("/category/{category}", response_model=schemas.analytics.CategoryStatsResponse)
def get_category_stats(category: str):
    category_stats = analytics_crud.get_category_stats(category)
    if not category_stats:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # category_stats = []
    # for category in category:
    #     category_stats.append(analytics_crud.get_all_category_stats())
    return category_stats

'''
Posibles analytics:

artículo con precio más barato y más caro por categoría
artículo con mayor descenso de precio registrado
artículo con mayor descenso de precio registrado por categoría
promedio de precio por categoría

📊 ESTADÍSTICAS RECOMENDADAS:
📈 Análisis de Precios:
Estadísticas generales (precio promedio, máximo, mínimo global)
Top productos más caros/baratos (por categoría y general)
Evolución de precios (promedio por mes/semana)
Distribución de precios por rangos
🔄 Análisis de Variaciones:
Productos con mayor volatilidad de precios
Mayores descensos de precio (ofertas/descuentos)
Mayores subidas de precio (productos en alza)
Productos sin cambios de precio (estables)
📊 Análisis por Categorías:
Comparativa entre categorías (promedio, rango)
Categoría más cara/barata
Categoría con más variabilidad
⏰ Análisis Temporal:
Tendencias por período (últimos 30/90 días)
Productos con cambios recientes
Frecuencia de cambios por producto
💡 CONSEJOS TÉCNICOS:
Usa agregaciones SQL (AVG, MAX, MIN, COUNT)
Considera paginación para endpoints grandes
Schemas específicos para cada tipo de estadística
Cacheable (estadísticas cambian poco)


'''