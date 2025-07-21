# utils/conversion.py
from schemas.articles import ArticleCreate
from scrap.schemas.schema_product import Product
from decimal import Decimal
from datetime import date

def product_to_articlecreate(item: Product) -> ArticleCreate:
    return ArticleCreate(
        category=item.category,
        rtr_id=int(item.rtr_id),
        name=item.name,
        price=Decimal(item.price),
        ean=int(item.ean) if item.ean else None,
        art_url=item.url,
        img_url=item.image_url,
        price_date=item.scraped_date if isinstance(item.scraped_date, date)
            else date.fromisoformat(item.scraped_date)
    )

def product_to_db_dict(item: Product):
    db_dict = {
        "categoria": item.category,
        "rtr_id": item.rtr_id,
        "nombre": item.name,
        "precio": item.price,
        "ean": item.ean,
        "art_url": item.url,
        "img_url": item.image_url,
        "fecha": item.scraped_date,
    }
    return db_dict