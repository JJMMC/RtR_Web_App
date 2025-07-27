from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database.crud_operations import article_crud, user_crud
from schemas.users import UserResponse, UserCreate, UserLogin
from auth import hashing_pw, jwt_gen
from fastapi.security import OAuth2PasswordRequestForm




router = APIRouter(
    prefix="/login",      # prefijo común para estas rutas
    tags=["Login"]        # agrupación en la documentación
)


@router.post('/')
def login_user(log_form: OAuth2PasswordRequestForm = Depends()):
    try:
        user_db = user_crud.get_user_by_usr_name(log_form.username)  # Usar username, no email
        
        # 1.-Comprobamos que el user_name esté en la DB
        if not user_db:
            raise HTTPException(
                status_code=401, 
                detail='Usuario o contraseña incorrectos'
                )
        
        # 2.-Comprobamos que la contraseña es correcta
        password_validation = hashing_pw.verify_password(log_form.password, user_db.hashed_password)
        if not password_validation:
            raise HTTPException(
                status_code=401, 
                detail='Usuario o contraseña incorrectos'
                )
        
        # 3.-Preparamos los datos para pasar al jwt_gen
        log_data = {'sub': user_db.user_name,
                    'user_id': user_db.id,
                    'role': user_db.role
                    }
        
        # 4.-Retornamos el token en formato estándar
        access_token = jwt_gen.create_access_token(log_data)
        return {"access_token": access_token, "token_type": "bearer"}
     
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")
    


