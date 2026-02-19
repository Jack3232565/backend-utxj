from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

# Importamos lo que está en la carpeta raíz
import database
import models
import security

router = APIRouter(
    tags=["Autenticación"]
)

@router.post("/token")
def login_para_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # 1. Buscamos al usuario en la BD
    usuario = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # 2. Validamos si existe y si la contraseña es correcta
    if not usuario or not security.verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Si todo está bien, generamos el Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    
    # 4. Devolvemos el token al usuario
    return {"access_token": access_token, "token_type": "bearer"}