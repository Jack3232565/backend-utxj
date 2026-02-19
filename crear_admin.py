from database import SessionLocal
import models
from security import get_password_hash

# 1. Abrimos conexión a la BD
db = SessionLocal()

# 2. Definimos los datos del Admin
nuevo_admin = models.User(
    username="admin",                 # Usuario
    hashed_password=get_password_hash("admin123"), # Contraseña (se encriptará)
    nombre_completo="Administrador UTXJ",
    rol="admin"
)

# 3. Intentamos guardarlo
try:
    # Verificamos si ya existe para no duplicar
    existe = db.query(models.User).filter(models.User.username == "admin").first()
    if not existe:
        db.add(nuevo_admin)
        db.commit()
        print("¡Usuario 'admin' creado exitosamente!")
    else:
        print("El usuario 'admin' ya existe.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    db.close()