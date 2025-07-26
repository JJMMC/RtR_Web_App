from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import logging


logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")  # Usa el endpoint de login

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Acces Token created")
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise Exception("Token inválido o expirado")
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)  # Usa tu función existente
        user_name = payload.get("sub")
        user_id = payload.get("user_id")
        if user_name is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return {"user_name": user_name, "user_id": user_id}
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
