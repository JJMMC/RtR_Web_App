from pydantic import BaseModel, HttpUrl, field_validator, Field
from typing import Any

class ScrapCategoriaModel(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre de la categoría")
    url: HttpUrl = Field(..., description="URL de la categoría")
    
    @field_validator('nombre', mode='before') # mode='before' se ejecuta antes de la validación de Pydantic
    @classmethod
    def validate_and_clean_nombre(cls, v: Any) -> str:
        """Valida y limpia el nombre de la categoría"""
        if v is None:
            raise ValueError('El nombre de la Categoría no puede ser None')
        
        # Convertir a string si no lo es
        nombre_str = str(v).strip()
        
        # Validar que no esté vacío
        if not nombre_str or len(nombre_str) < 1:
            raise ValueError('El nombre no puede estar vacío')
        
        # Limpiar caracteres especiales si es necesario
        nombre_limpio = nombre_str.replace('\n', ' ').replace('\t', ' ')
        
        # Eliminar espacios múltiples
        while '  ' in nombre_limpio:
            nombre_limpio = nombre_limpio.replace('  ', ' ')
            
        return nombre_limpio.strip()
    
    @field_validator('url', mode='before')
    @classmethod
    def validate_and_process_url(cls, v: Any) -> str:
        """Valida y procesa la URL de la categoría"""
        if v is None:
            raise ValueError('La URL no puede ser None')
        
        # Manejar diferentes tipos de input que puede devolver BeautifulSoup
        if isinstance(v, list):
            # Si get("href") devuelve una lista, tomar el primer elemento
            url_str = str(v[0]) if v and len(v) > 0 else ""
        elif hasattr(v, '__iter__') and not isinstance(v, str):
            # Si es iterable pero no string, convertir el primer elemento
            try:
                url_str = str(next(iter(v)))
            except (StopIteration, TypeError):
                url_str = str(v)
        else:
            # Conversión directa a string
            url_str = str(v)
        
        # Limpiar la URL
        url_str = url_str.strip()
        
        # if not url_str:
        #     raise ValueError('La URL no puede estar vacía')
        
        # # Manejar URLs relativas - convertir a absolutas
        # if url_str.startswith('/'):
        #     # Asumiendo que tienes una base URL en config
        #     try:
        #         from config import main_url
        #         base_url = main_url.rstrip('/')
        #         url_str = base_url + url_str
        #     except ImportError:
        #         # Fallback si no existe config
        #         url_str = "https://example.com" + url_str
        
        # # Validar que la URL tiene formato correcto
        # if not url_str.startswith(('http://', 'https://')):
        #     raise ValueError(f'URL debe comenzar con http:// o https://. Recibido: {url_str}')
        
        return url_str
    
    model_config = {
        "str_strip_whitespace": True,  # Elimina espacios automáticamente
        "validate_assignment": True,   # Valida al asignar valores
        "json_schema_extra": {
            "example": {
                "nombre": "Electrónica",
                "url": "https://example.com/electronica"
            }
        }
    }