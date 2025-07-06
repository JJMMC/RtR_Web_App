import requests
from bs4 import BeautifulSoup
from scrap.utils.config import headers, main_url

url = main_url

## GENERADORES ##
#Función generador de sopas
def soup_generator(url):
    try:
        res = requests.get(url,headers=headers, timeout=10)
        res.raise_for_status()
        content = res.text
        soup = BeautifulSoup(content, "html.parser")
        return soup
    except requests.RequestException as e: #Falta definir ¿qué pasa si la url no se ha scrapeado
        print(f"Error fetching {url}: {e}")
        return None

#print(soup_generator(url))