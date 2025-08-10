from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database.crud_operations import article_crud, price_record_crud, analytics_crud

app = FastAPI()

# Configura los templates y los archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_page": "home"})

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    products = article_crud.get_active()  # Obtén los productos de tu backend
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "active_page": "products"
    })

@app.get("/products/search", response_class=HTMLResponse)
async def search_products(request: Request, q: str = ""):
    if q:
        filtered = [p for p in article_crud.get_active() if q.lower() in p.name.lower() or q.lower() in p.category.lower()]
    else:
        filtered = article_crud.get_active()
    return templates.TemplateResponse("partials/product_list.html", {
        "request": request,
        "products": filtered,
        "active_page": "products"
    })


@app.get("/products/{rtr_id}", response_class=HTMLResponse)
async def product_detail(request: Request, rtr_id: int):
    # Obtén el producto por su rtr_id
    product = article_crud.get_by_rtr_id(rtr_id)
    # Obtén el historial de precios (ajusta según tu modelo)
    price_history = price_record_crud.get_price_history(rtr_id)
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "price_history": price_history,
        "active_page": "products"
    })


@app.get("/price-drop", response_class=HTMLResponse)
def price_drop(request: Request):
    products = analytics_crud.get_products_with_price_drop()
    return templates.TemplateResponse("price_drop.html", {
        "request": request,
        "products": products
    })