from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.crud_operations import article_crud

app = FastAPI()

# Configura los templates y los archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    products = article_crud.get_all()  # Obtén los productos de tu backend
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products
    })

@app.get("/products/search", response_class=HTMLResponse)
async def search_products(request: Request, q: str = ""):
    if q:
        filtered = [p for p in article_crud.get_all() if q.lower() in p.name.lower() or q.lower() in p.category.lower()]
    else:
        filtered = article_crud.get_all()
    return templates.TemplateResponse("partials/product_list.html", {
        "request": request,
        "products": filtered
    })