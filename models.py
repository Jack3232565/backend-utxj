from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base

# ---------------------------------------------------------
# TABLA 1: ADMINISTRADORES (Para el Login)
# ---------------------------------------------------------
class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) # Aquí guardaremos la contraseña encriptada
    nombre_completo = Column(String(100))
    rol = Column(String(20), default="admin") # Por si a futuro hay más roles

# ---------------------------------------------------------
# TABLA 2: PROSPECTOS / ALUMNOS
# ---------------------------------------------------------
class Prospecto(Base):
    __tablename__ = "prospectos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Fecha automática de cuando se llenó el registro
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Datos Personales
    nombre = Column(String(100), nullable=False)
    ap_paterno = Column(String(100), nullable=False)
    ap_materno = Column(String(100), nullable=False)
    localidad_origen = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=False)

    # Carrera de Interés (Guardaremos el texto exacto que elijan)
    # Opciones: 
    # - T.S.U. Mantenimiento Industrial
    # - T.S.U. Mantenimiento Petróleo
    # - T.S.U. Mantenimiento Soldadura
    # - Ingeniería en Mantenimiento Industrial
    carrera_interes = Column(String(150), nullable=False)

    # Visita al Área
    visita_industrial = Column(Boolean, default=False) # ¿Quiere visita? Sí/No
    
    # Agenda (Solo se llena si visita_industrial es True)
    # Puede ser NULL si no quieren visita
    fecha_agenda = Column(DateTime, nullable=True) 
    
    # Campo extra por si quieres agregar notas internas del admin
    notas_admin = Column(Text, nullable=True)

    # NUEVA COLUMNA:
    preinscrito = Column(Boolean, default=False)

    # NUEVA COLUMNA
    contactado = Column(Boolean, default=False)