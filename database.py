from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA CONEXIÓN
# ---------------------------------------------------------
# Reemplaza con tus datos reales de MySQL Workbench:
# USUARIO: por lo general es 'root'
# CONTRASEÑA: la que configuraste al instalar MySQL
# HOST: usualmente 'localhost' o '127.0.0.1'
# PUERTO: por defecto es 3306
# NOMBRE_BD: el nombre que le daremos a tu base de datos (ej. 'utxj_mantenimiento')

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/utxj_mantenimiento"
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_tOf39RjPQFsb@ep-polished-poetry-ai7qjpge-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"


# Creamos el "motor" de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Creamos una "fábrica" de sesiones.
# Cada vez que alguien entre a la app, se crea una sesión temporal.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta clase 'Base' será el molde para nuestros modelos (tablas) más adelante
Base = declarative_base()

# ---------------------------------------------------------
# FUNCIÓN DE UTILIDAD (Dependencia)
# ---------------------------------------------------------
# Esta función se asegura de cerrar la conexión a la BD
# incluso si ocurre un error, para no dejar conexiones "colgadas".
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()