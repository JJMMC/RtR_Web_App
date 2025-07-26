from fastapi import FastAPI, HTTPException, Query
#import schemas
from typing import List
from datetime import date
from decimal import Decimal
from database.crud_operations import article_crud
from database.db_session import db_manager
from database.db_models import Article
from sqlalchemy import select
from routers import articles, categories, analytics, users, login

app = FastAPI()

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(login.router)


@app.get("/", tags=["Index"])
def index():
    print('Index page')
    return {'message': 'Index page'}

   