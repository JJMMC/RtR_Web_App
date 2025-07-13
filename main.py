from fastapi import FastAPI, HTTPException, Query
#import schemas
from typing import List
from datetime import date
from decimal import Decimal
from database.crud_operations import articulo_crud
from database.db_session import db_manager
from database.db_models import Articulo
from sqlalchemy import select
from routers import articles, categories, analytics

app = FastAPI()

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(analytics.router)


@app.get("/")
def index():
    print('Index page')
    return {'message': 'Index page'}

   