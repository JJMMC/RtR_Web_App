from bs4 import BeautifulSoup, Tag
from datetime import datetime
from config import main_url
from soup_gen import soup_generator
from scrap.schema_cat_url import ScrapCategoriaModel
from pydantic import ValidationError

## OBTENIENDO URLS ##
# Función para obtener las CAT y CAT_URLS
def request_categorias_and_main_urls(url=main_url):
    soup = soup_generator(url)
    if not soup:
        return
    
    try:
        # Capturamos toda la barra lateral con las categorías y sub-categorías
        menu_ul = soup.find("ul", class_="category-sub-menu")
        if not menu_ul:
            print('Side menu not found')
            return
        
        # Obtenemos las urls de Categorias y subcategorias
        all_categories = menu_ul.find_all("a")  # type: ignore
        sub_categories = menu_ul.find_all("a", class_="category-sub-link")  # type: ignore
        
        # Filtrar solo las categorías principales (sin subcategorías)
        main_categories = [url for url in all_categories if url not in sub_categories]
        
        # Procesar cada categoría - DEJAR QUE PYDANTIC HAGA TODO EL TRABAJO
        for elemento in main_categories:
            try:
                # Extraer datos mínimos - Pydantic validará y convertirá
                categoria_validada = ScrapCategoriaModel(
                    nombre=elemento.get_text(strip=True),
                    url=elemento.get("href") # type: ignore
                )
                
                # Yield de la categoría validada
                yield categoria_validada.nombre, str(categoria_validada.url)
                
            except ValidationError as e:
                # Solo imprimir si quieres debug, sino solo continue
                print(f"Categoría inválida saltada: {e}")
                continue
                
    except Exception as e:
        print(f"Error general: {e}")
        return

# Función que dada la cat_url de la categoria retorna list() de las urls (páginas) que descuelgan de ella para extraer los datos
def find_child_urls(cat_url):
    for i in range(1, 10):
        test_url = f"{cat_url}?page={str(i)}"
        soup = soup_generator(test_url)
        if not soup:
            continue
        vacio = soup.find(class_="page-content page-not-found")
        if vacio is None:
            yield test_url
        else:
            break





if __name__ == ("__main__"):
    result = request_categorias_and_main_urls()
    for categoria, url in result:
        print('Categoria: ',categoria, 'Url: ', url ) 
        childs_in_cat = find_child_urls(url)
        for url in childs_in_cat:
            print(url)