from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import pandas as pd
import io

# Importamos todo lo necesario
import database
import models
import schemas
import security

router = APIRouter(
    prefix="/admin",
    tags=["Panel Administrativo"],
    dependencies=[Depends(security.get_current_user)] # Todo aquí requiere Token
)

# ---------------------------------------------------------
# 1. CARGA MASIVA DE EXCEL (Con Auto-Formateo de Texto)
# ---------------------------------------------------------
@router.post("/upload-excel")
async def cargar_excel(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un Excel (.xlsx)")
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        df = df.where(pd.notnull(df), None)
        registros = 0
        for index, row in df.iterrows():
                    
                    # Limpiamos el teléfono quitando espacios y guiones automáticamente
                    tel_limpio = str(row.get('Telefono', '')).replace(' ', '').replace('-', '').strip()
                    # Si al final quedan decimales (ej. 7762315280.0), los quitamos
                    if tel_limpio.endswith('.0'):
                        tel_limpio = tel_limpio[:-2]

                    nuevo = models.Prospecto(
                        nombre=str(row.get('Nombre', 'S/N')).strip().title(),
                        ap_paterno=str(row.get('Apellido Paterno', '')).strip().title(),
                        ap_materno=str(row.get('Apellido Materno', '')).strip().title(),
                        localidad_origen=str(row.get('Localidad', '')).strip().title(),
                        telefono=tel_limpio, # <--- USAMOS EL TELÉFONO LIMPIO AQUÍ
                        carrera_interes=str(row.get('Carrera', 'T.S.U. Mantenimiento Industrial')).strip(),
                        visita_industrial=False,
                        notas_admin="Importado Excel",
                        preinscrito=False,
                        contactado=False
                    )
                    db.add(nuevo)
                    registros += 1
            
        db.commit()
        return {"mensaje": f"Importados {registros} registros."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
# 2. CRUD: ACTUALIZAR Y ELIMINAR (Con Auto-Formateo)
# ---------------------------------------------------------

# EDITAR un alumno existente
@router.put("/prospectos/{id}")
def actualizar_prospecto(id: int, datos: schemas.ProspectoCreate, db: Session = Depends(database.get_db)):
    prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not prospecto:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # AQUÍ TAMBIÉN LIMPIAMOS LOS DATOS AL EDITAR
    prospecto.nombre = datos.nombre.strip().title() if datos.nombre else ""
    prospecto.ap_paterno = datos.ap_paterno.strip().title() if datos.ap_paterno else ""
    prospecto.ap_materno = datos.ap_materno.strip().title() if datos.ap_materno else ""
    prospecto.localidad_origen = datos.localidad_origen.strip().title() if datos.localidad_origen else ""
    
    prospecto.telefono = datos.telefono
    prospecto.carrera_interes = datos.carrera_interes
    prospecto.visita_industrial = datos.visita_industrial
    prospecto.fecha_agenda = datos.fecha_agenda
    prospecto.notas_admin = datos.notas_admin 
    prospecto.preinscrito = datos.preinscrito
    prospecto.contactado = datos.contactado # <--- AGREGAR AQUÍ 
    
    db.commit()
    return {"mensaje": "Alumno actualizado correctamente"}

# ELIMINAR un alumno
@router.delete("/prospectos/{id}")
def eliminar_prospecto(id: int, db: Session = Depends(database.get_db)):
    prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not prospecto:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    db.delete(prospecto)
    db.commit()
    return {"mensaje": "Alumno eliminado del sistema"}

# ---------------------------------------------------------
# 3. ESTADÍSTICAS AVANZADAS
# ---------------------------------------------------------
@router.get("/dashboard-stats")
def obtener_estadisticas(db: Session = Depends(database.get_db)):
    # A. Total
    total = db.query(models.Prospecto).count()
    
    # B. Por Carrera
    por_carrera = db.query(models.Prospecto.carrera_interes, func.count(models.Prospecto.id))\
        .group_by(models.Prospecto.carrera_interes).all()
        
    # C. Por Visita (Sí vs No)
    por_visita = db.query(models.Prospecto.visita_industrial, func.count(models.Prospecto.id))\
        .group_by(models.Prospecto.visita_industrial).all()

    # D. Por Localidad (Top 10)
    por_localidad = db.query(models.Prospecto.localidad_origen, func.count(models.Prospecto.id))\
        .group_by(models.Prospecto.localidad_origen)\
        .order_by(desc(func.count(models.Prospecto.id)))\
        .limit(10).all()
    
    # E. Preinscritos por carrera
    por_preinscrito = db.query(models.Prospecto.carrera_interes, func.count(models.Prospecto.id))\
        .filter(models.Prospecto.preinscrito == True)\
        .group_by(models.Prospecto.carrera_interes).all()

    return {
        "total": total,
        "carreras": { "labels": [p[0] for p in por_carrera], "data": [p[1] for p in por_carrera] },
        "visitas": { "labels": ["Sí", "No"], "data_raw": [{"estado": p[0], "total": p[1]} for p in por_visita] },
        "localidades": { "labels": [p[0] for p in por_localidad], "data": [p[1] for p in por_localidad] },
        "preinscritos": { "labels": [p[0] for p in por_preinscrito], "data": [p[1] for p in por_preinscrito] }
    }