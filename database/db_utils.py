from typing import List, Dict, Any, Tuple

def scraped_to_dict(list_productos_tuplas: List[Tuple]) -> List[Dict[str, Any]]:
    """
    Convertir datos scrapeados a diccionarios
    Mantiene la misma funcionalidad que tu función original
    """
    scraped_dict_lst = []
    for cat, rtr_id, nombre, precio, ean, art_url, img_url, fecha in list_productos_tuplas:
        producto = {
            'categoria': cat,
            'rtr_id': rtr_id,
            'nombre': nombre,
            'precio': precio,
            'ean': ean,
            'art_url': art_url,
            'img_url': img_url,
            'fecha': fecha
        }
        scraped_dict_lst.append(producto)
    return scraped_dict_lst

def separate_article_and_price_data(product_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Separar datos de artículo y precio"""
    article_data = {
        'categoria': product_data['categoria'],
        'rtr_id': product_data['rtr_id'],
        'nombre': product_data['nombre'],
        'ean': product_data['ean'],
        'art_url': product_data['art_url'],
        'img_url': product_data['img_url']
    }
    
    price_data = {
        'rtr_id': product_data['rtr_id'],
        'precio': product_data['precio'],
        'fecha': product_data['fecha']
    }
    
    return article_data, price_data