from fastapi import FastAPI, HTTPException
import schemas as schemas
from typing import List
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
    

