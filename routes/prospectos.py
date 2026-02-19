from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime 
from typing import List

import models
import schemas
import database
import security

router = APIRouter(
    prefix="/prospectos",
    tags=["Prospectos"]
)

@router.post("/", response_model=schemas.Prospecto)
def crear_prospecto(prospecto: schemas.ProspectoCreate, db: Session = Depends(database.get_db)):
    
    # 1. SEGURIDAD ANTI-DUPLICADOS (Teléfono)
    telefono_existente = db.query(models.Prospecto).filter(models.Prospecto.telefono == prospecto.telefono).first()
    if telefono_existente:
        raise HTTPException(status_code=400, detail="Este número de teléfono ya se encuentra registrado.")
    
    # 2. VALIDACIÓN ESTRICTA DE HORARIO DE CITAS
    if prospecto.visita_industrial and prospecto.fecha_agenda:
        fecha_cita = prospecto.fecha_agenda
        if isinstance(fecha_cita, str):
            try:
                fecha_cita = datetime.fromisoformat(fecha_cita)
            except ValueError:
                pass 
        
        if isinstance(fecha_cita, datetime):
            if fecha_cita.weekday() > 4: 
                raise HTTPException(status_code=400, detail="Las citas solo pueden agendarse de Lunes a Viernes.")
            
            minutos_desde_medianoche = (fecha_cita.hour * 60) + fecha_cita.minute
            inicio_permitido = 9 * 60          
            fin_permitido = (15 * 60) + 30     
            
            if minutos_desde_medianoche < inicio_permitido or minutos_desde_medianoche > fin_permitido:
                raise HTTPException(status_code=400, detail="El horario de atención para visitas es estrictamente de 9:00 AM a 3:30 PM.")

    # 3. GUARDAR EL REGISTRO CON AUTO-FORMATEO DE MAYÚSCULAS
    db_prospecto = models.Prospecto(
        # APLICAMOS LA REGLA .title() AQUÍ:
        nombre=prospecto.nombre.strip().title() if prospecto.nombre else "",
        ap_paterno=prospecto.ap_paterno.strip().title() if prospecto.ap_paterno else "",
        ap_materno=prospecto.ap_materno.strip().title() if prospecto.ap_materno else "",
        localidad_origen=prospecto.localidad_origen.strip().title() if prospecto.localidad_origen else "",
        
        telefono=prospecto.telefono,
        carrera_interes=prospecto.carrera_interes,
        visita_industrial=prospecto.visita_industrial,
        fecha_agenda=prospecto.fecha_agenda,
        notas_admin=prospecto.notas_admin,
        preinscrito=prospecto.preinscrito,
        contactado=prospecto.contactado # <--- AGREGAR ESTA LÍNEA
        
    )
    db.add(db_prospecto)
    db.commit()
    db.refresh(db_prospecto)
    return db_prospecto

@router.get("/", response_model=list[schemas.Prospecto])
def leer_prospectos(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    prospectos = db.query(models.Prospecto).offset(skip).limit(limit).all()
    return prospectos