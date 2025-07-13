from fastapi import APIRouter, HTTPException
# import schemas
from typing import List
from database.crud_operations import articulo_crud
# from database.db_session import db_manager
# from database.db_models import Articulo
# from sqlalchemy import select


router = APIRouter(
    prefix="/categories",      # prefijo común para estas rutas
    tags=["Categories"]        # agrupación en la documentación
)


@router.get('/', response_model= List[str])
def get_categories():
    """Obtener todos las Categorías"""
    try:
        categories = articulo_crud.get_all_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")
