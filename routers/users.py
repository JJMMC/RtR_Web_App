from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database.crud_operations import article_crud, user_crud
from schemas.users import UserResponse, UserCreate, UserLogin
from auth import hashing_pw, jwt_gen

router = APIRouter(
    prefix="/users",      # prefijo común para estas rutas
    tags=["Users"]        # agrupación en la documentación
)


@router.post('/', response_model= UserResponse)
def create_user(user_data: UserCreate):
    """Crear un nuevo usuario"""
    try:
        user_dict = dict(user_data)
        user_dict['hashed_password'] = hashing_pw.hash_password(user_dict.pop('password'))
        user = user_crud.insert_user(user_dict)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving articles: {str(e)}")

@router.get("/private")
def private_route(current_user: dict = Depends(jwt_gen.get_current_user)):
    return {"msg": f"Hola {current_user['user_name']}, accediste a una ruta protegida"}