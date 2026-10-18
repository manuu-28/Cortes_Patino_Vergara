"""
Deja la base como recién instalada: borra todas las tablas, las vuelve a crear,
aplica los scripts sql/01-03 y carga los datos de prueba (sql/04).

Úselo antes de tomar las capturas de evidencias, para que los resultados
coincidan con los cálculos a mano.

Uso (con el venv activo, dentro de la carpeta backend):  python reiniciar_base.py
La API puede seguir encendida mientras lo ejecuta.
"""
from sqlalchemy import text

from app import models  # noqa: F401  (registra las entidades)
from app.database import Base, engine
from main import aplicar_scripts_sql

with engine.begin() as conexion:
    conexion.execute(text("DROP SCHEMA public CASCADE"))
    conexion.execute(text("CREATE SCHEMA public"))

Base.metadata.create_all(bind=engine)
aplicar_scripts_sql()

import cargar_datos  # noqa: E402,F401  (ejecuta la carga al importarse)

print("Base reiniciada con los datos de prueba.")
