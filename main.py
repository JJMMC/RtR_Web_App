from fastapi import FastAPI, HTTPException, Query
import schemas
from typing import List
from datetime import date
from decimal import Decimal
from database.crud_operations import articulo_crud
from database.db_session import db_manager
from database.db_models import Articulo
from sqlalchemy import select

app = FastAPI()


@app.get("/")
def index():
    print('Index page')
    return {'message': 'Index page'}

@app.get("/article/{article_id}", response_model=schemas.ArticuloResponse)
def article_by_id(article_id: int):
    """Obtener artículo básico por ID"""
    try:
        article = articulo_crud.get_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving article: {str(e)}")

@app.get("/all_data_article/{article_id}", response_model=schemas.ArticuloFullData)
def all_data_article_by_id(article_id: int):
    """Obtener artículo con historial completo por ID"""
    with db_manager.get_session() as session:
        try:
            article = session.scalar(
                select(Articulo).filter(Articulo.id == article_id)
            )
            
            if article is None:
                raise HTTPException(status_code=404, detail="Article not found")
            
            # Construir respuesta con historial
            article_data = {
                "id": article.id,
                "rtr_id": article.rtr_id,
                "categoria": article.categoria,
                "nombre": article.nombre,
                "ean": article.ean,
                "art_url": article.art_url,
                "img_url": article.img_url,
                "historial_precios": [
                    {
                        "id": precio.id,
                        "precio": precio.precio,
                        "fecha": precio.fecha,
                    }
                    for precio in article.historial
                ]
            }
            
            return schemas.ArticuloFullData.model_validate(article_data)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving article data: {str(e)}")

@app.get("/articles", response_model=List[schemas.ArticuloResponse])
def get_all_articles():
    """Obtener todos los artículos"""
    try:
        articles = articulo_crud.get_all()
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")
    
@app.post("/articles", response_model=schemas.ArticuloResponse)
def create_article(article: schemas.ArticuloCreate):
    
    # 1.-Convertimosa dicciónario
    product_data = dict(article)
    print(product_data)
    print(type(product_data))
    

    # 2.-Comprobamos que no exista ya el artículo:
    
    if articulo_crud.exists_by_rtr_id(article.rtr_id):
        print('Artículo ya declarado en la DB')
        raise HTTPException(409, "Already exists")
    
    # 3.-Insertamos el artículo en la db
    articulo_crud.insert_one(product_data)

    # 4.-Retornamos el artículo introducido
    product_data_rtned = articulo_crud.get_by_rtr_id(article.rtr_id)
    
    # ✅ Verificar explícitamente que no es None:
    if product_data_rtned is None:
        raise HTTPException(status_code=500, detail="Article created but not found")
    
    # Damos los valores según las necesidades de reponse model de pydantic
    return {
        "id": product_data_rtned.id,  
        "rtr_id": product_data_rtned.rtr_id,
        "categoria": product_data_rtned.categoria,
        "nombre": product_data_rtned.nombre,
        "ean": product_data_rtned.ean,
        "art_url": product_data_rtned.art_url,
        "img_url": product_data_rtned.img_url
    }


@app.put("/articles/{article_id}", response_model=schemas.ArticuloResponse)
def update_article(article_id: int, update_data: schemas.ArticuloUpdate):
    try:
        # 1.- Obtenemos el artículo a actualizar
        update_dic = dict(update_data)

        # 2.- Actualizamos el artíuclo en la db
        updated_article = articulo_crud.update_one(article_id, update_dic)
        
        # 3. Retornar el resultado
        return updated_article
        
    except ValueError as e:  # Si no existe el artículo
        raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating article: {str(e)}")


@app.get('/articles/search', response_model=List[schemas.ArticuloFullData])
def search_article(
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
        if nombre: filters['nombre'] = nombre
        if rtr_id: filters['rtr_id'] = rtr_id
        if categoria: filters['categoria'] = categoria
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
        # 3. Validar que precio y fecha sean coherentes
        if 'min_price' in filters and 'max_price' in filters:
            if filters['min_price'] > filters['max_price']:
                raise HTTPException(400, "min_price cannot be greater than max_price")
        
        if 'min_date' in filters and 'max_date' in filters:
            if filters['min_date'] > filters['max_date']:
                raise HTTPException(400, "min_date cannot be greater than max_date")



        # 4. Llamar al CRUD real (cuando esté implementado)
        results = articulo_crud.search(filters, limit=limit)
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error searching articles: {str(e)}"
        )