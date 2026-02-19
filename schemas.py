from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Esto define QUÉ datos esperamos recibir del formulario Vue
class ProspectoBase(BaseModel):
    nombre: str
    ap_paterno: str
    ap_materno: str
    localidad_origen: str
    telefono: str
    carrera_interes: str  # TSU Mantenimiento, Petróleo, etc.
    visita_industrial: bool = False
    fecha_agenda: Optional[datetime] = None
    notas_admin: Optional[str] = None
    # NUEVO CAMPO:
    preinscrito: bool = False
    contactado: bool = False

# Para crear (usamos la base)
class ProspectoCreate(ProspectoBase):
    pass

# Para leer (devuelve lo mismo + el ID y la fecha de registro)
class Prospecto(ProspectoBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True