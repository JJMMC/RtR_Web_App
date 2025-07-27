from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database.crud_operations import article_crud, user_crud
from schemas.users import UserResponse, UserCreate, UserLogin, UserUpdate
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
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@router.get('/', response_model= UserResponse)
def get_user(current_user: dict = Depends(jwt_gen.get_current_user)):
    """Obtener el usuario actual"""
    try:
        user_data = user_crud.get_user_by_id(current_user['user_id'])
        return user_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


@router.put('/', response_model= UserResponse)
def update_user(data_to_update: UserUpdate, current_user: dict = Depends(jwt_gen.get_current_user)):
    """Actualizar el usuario actual"""
    try:
        user_id = current_user['user_id']
        data_to_update_dict = dict(data_to_update)
        updated_user = user_crud.update_user_by_id(user_id, data_to_update_dict)        
        return updated_user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


@router.delete('/', response_model=UserResponse)
def delete_user(current_user: dict = Depends(jwt_gen.get_current_user)):
    """Eliminar un usuario actual"""
    try:
        # 1.-Obtenemos el usuario a eliminar
        user_erased = user_crud.get_user_by_id(current_user['user_id'])
        
        # 2.-Eliminamos el usuario
        if not user_crud.remove_user_by_id(current_user['user_id']):
            raise HTTPException(status_code=404, detail="Usuario no encontrado o no se pudo eliminar") 
        return user_erased
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@router.get("/private")
def private_route(current_user: dict = Depends(jwt_gen.get_current_user)):
    return {"msg": f"Hola {current_user['user_name']}, accediste a una ruta protegida"}

