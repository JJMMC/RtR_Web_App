from fastapi import APIRouter, HTTPException, Query
import schemas.articles
from typing import List
from datetime import date
from decimal import Decimal
from database.crud_operations import article_crud
from database.db_session import db_manager
from database.db_models import Article
from sqlalchemy import select


router = APIRouter(
    prefix="/articles",      # prefijo común para estas rutas
    tags=["Articles"]        # agrupación en la documentación
)


#### SEARCH ENDPOINTS
@router.get('/search', response_model=List[schemas.articles.ArticleResponse])
def search_article(
    nombre: str = Query(None, min_length=2, description="Product name"),
    rtr_id: int = Query(None, gt=0, description="RTR ID"),
    categoria: str = Query(None, description="Category"),
    ean: str = Query(None, min_length=8, description="EAN code"),
    limit: int = Query(20, ge=1, le=100, description="Max results (1-100)")
    ): # Utilizamos Query en lugar de pydantic schema para validar ya que se entiende mejor con swagger y FastAPI para este tipo de consulta

    try:
        # 1. Construir filters
        filters = {}
        if nombre: filters['name'] = nombre
        if rtr_id: filters['rtr_id'] = rtr_id
        if categoria: filters['category'] = categoria
        if ean: filters['ean'] = ean

        # 2. Validar que hay al menos un filtro
        if not filters:
            raise HTTPException(
                status_code=400, 
                detail="At least one search parameter is required"
            )

        # 4. Llamar al CRUD 
        results = article_crud.search(filters, limit=limit)

        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching articles: {str(e)}"
        )

@router.get('/search/history', response_model=List[schemas.articles.ArticleFullData])
def search_article_history(
    nombre: str = Query(None, min_length=2, description="Product name"),
    rtr_id: int = Query(None, gt=0, description="RTR ID"),
    categoria: str = Query(None, description="Category"),
    ean: str = Query(None, min_length=8, description="EAN code"),
    min_price: Decimal = Query(None, ge=0, description="Min price"),
    max_price: Decimal = Query(None, gt=0, description="Max price"),
    min_date: date = Query(None, description="From date"),
    max_date: date = Query(None, description="To date"),
    limit: int = Query(20, ge=1, le=100, description="Max results (1-100)")
    ):

    try:
        # 1. Construir filters
        filters = {}
        if nombre: filters['name'] = nombre
        if rtr_id: filters['rtr_id'] = rtr_id
        if categoria: filters['category'] = categoria
        if ean: filters['ean'] = ean
        if min_price: filters['min_price'] = min_price
        if max_price: filters['max_price'] = max_price
        if min_date: filters['min_date'] = min_date
        if max_date: filters['max_date'] = max_date

        # 2. Validar que hay al menos un filtro
        if not filters:
            raise HTTPException(
                status_code=400, 
                detail="At least one search parameter is required"
            )
        # 3. Validar que al menos un filtro de precio o fecha existe.
        if 'min_price' not in filters and 'max_price' not in filters and 'min_date' not in filters and 'max_date' not in filters:
            raise HTTPException(400, "No price or date filter")

        # 4. Validar que precio y fecha sean coherentes
        if 'min_price' in filters and 'max_price' in filters:
            if filters['min_price'] > filters['max_price']:
                raise HTTPException(400, "min_price cannot be greater than max_price")

        if 'min_date' in filters and 'max_date' in filters:
            if filters['min_date'] > filters['max_date']:
                raise HTTPException(400, "min_date cannot be greater than max_date")

        # 4. Llamar al CRUD 
        results = article_crud.search_with_history(filters, limit=limit)

        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching articles: {str(e)}"
        )


#### BASIC CRUD ENDPOINTS
@router.get("/", response_model=List[schemas.articles.ArticleResponse])
def get_all_articles():
    """Obtener todos los artículos"""
    try:
        articles = article_crud.get_all()
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")

@router.post("/", response_model=schemas.articles.ArticleResponse)
def create_article(article: schemas.articles.ArticleCreate):
    
    # 1.-Convertimosa dicciónario
    product_data = dict(article)
    print(product_data)
    print(type(product_data))
    

    # 2.-Comprobamos que no exista ya el artículo:
    
    if article_crud.exists_by_rtr_id(article.rtr_id):
        print('Artículo ya declarado en la DB')
        raise HTTPException(409, "Already exists")
    
    # 3.-Insertamos el artículo en la db
    article_crud.insert_one_with_price(product_data)

    # 4.-Retornamos el artículo introducido
    product_data_rtned = article_crud.get_by_rtr_id(article.rtr_id)
    
    # ✅ Verificar explícitamente que no es None:
    if product_data_rtned is None:
        raise HTTPException(status_code=500, detail="Article created but not found")
    
    return schemas.articles.ArticleResponse.model_validate(product_data_rtned)

@router.put("/{rtr_id}", response_model=schemas.articles.ArticleResponse)
def update_article(rtr_id: int, update_data: schemas.articles.ArticleUpdate):
    try:
        # 1.- Obtenemos el artículo a actualizar
        update_dic = dict(update_data)

        # 2.- Actualizamos el artíuclo en la db
        updated_article = article_crud.update_one(rtr_id, update_dic)
        
        # 3. Retornar el resultado
        return updated_article
        
    except ValueError as e:  # Si no existe el artículo
        raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating article: {str(e)}")

@router.get("/all_data/{article_id}", response_model=schemas.articles.ArticleFullData)
def article_by_id_all_data(article_id: int):
    """Obtener artículo con historial completo por ID"""
    with db_manager.get_session() as session:
        try:
            article = session.scalar(
                select(Article).filter(Article.id == article_id)
            )
            
            if article is None:
                raise HTTPException(status_code=404, detail="Article not found")
            
            return schemas.articles.ArticleFullData.model_validate(article)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving article data: {str(e)}")

@router.get("/{article_id}", response_model=schemas.articles.ArticleResponse)
def article_by_id(article_id: int):
    """Obtener artículo básico por ID"""
    try:
        article = article_crud.get_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving article: {str(e)}")
    




    




