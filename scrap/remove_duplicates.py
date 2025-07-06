from typing import List, Tuple

def remove_duplicates_by_id(products_list: List[Tuple]) -> List[Tuple]:
    """
    Elimina duplicados usando set para tracking eficiente de IDs únicos.
    
    Args:
        products_list: Lista de tuplas donde products_list[i][1] es el rtr_id
        
    Returns:
        Lista de productos únicos sin duplicados
    """
    seen_ids = set()
    unique_products = []
    duplicates = []
    
    for product_tuple in products_list:
        # product_tuple[1] es rtr_id en mi estructura
        rtr_id = product_tuple[1]
        
        if rtr_id not in seen_ids:
            seen_ids.add(rtr_id)
            unique_products.append(product_tuple)
        else:
            duplicates.append(rtr_id)
    
    # Log para debug
    if duplicates:
        print(f"🔍 IDs duplicados encontrados: {duplicates}")
    
    print(f"✅ Productos únicos: {len(unique_products)}")
    print(f"🗑️  Duplicados eliminados: {len(duplicates)}")
    
    return unique_products

def get_duplicate_stats(products_list: List[Tuple]) -> dict:
    """Retorna estadísticas de duplicados sin eliminarlos"""
    seen_ids = set()
    duplicates = []
    
    for product_tuple in products_list:
        rtr_id = product_tuple[1]
        if rtr_id in seen_ids:
            duplicates.append(rtr_id)
        else:
            seen_ids.add(rtr_id)
    
    return {
        'total_products': len(products_list),
        'unique_products': len(seen_ids),
        'duplicates_count': len(duplicates),
        'duplicate_ids': duplicates
    }

