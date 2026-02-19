from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORTANTE PARA VUE
import models
from database import engine

# --- IMPORTAMOS LA NUEVA RUTA ---
from routes import prospectos, auth, admin# <--- Agrega 'auth' aquí

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Mantenimiento UTXJ",
    description="Sistema de captación de alumnos y visitas industriales",
    version="1.0.0"
)

# --- CONFIGURACIÓN CORS ---
# Esto permite que tu Frontend (Vue) que correrá en el puerto 5173
# pueda hablar con tu Backend (Python) en el puerto 8000.
origins = [
    "http://localhost:5173",
    "https://frontend-utxj.vercel.app",
    "https://frontend-utxj-jijzlpl9d-carlos-ivan-s-projects.vercel.app", # Tu URL de Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUIMOS EL ROUTER ---
app.include_router(auth.router)        # <--- ¡NUEVA LÍNEA!
app.include_router(prospectos.router)
app.include_router(admin.router) # <--- Conectamos admin

@app.get("/")
def read_root():

    return {"mensaje": "API UTXJ operando correctamente"}
