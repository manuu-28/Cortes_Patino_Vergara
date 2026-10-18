"""
Punto de entrada de la API NexoEventos.

Al arrancar:
  1. Crea las tablas a partir de las entidades (Base.metadata.create_all).
  2. Aplica los scripts de sql/ en orden: triggers y funciones (01), reportes (02)
     y catálogo oficial (03). Son idempotentes: se pueden aplicar en cada arranque.
     Los datos de prueba (04) NO se cargan aquí: se cargan con cargar_datos.py.
  3. Registra los routers y el manejo de errores.

Ejecutar:  uvicorn main:app --reload      ->  documentación en http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app import models  # noqa: F401  (registra las entidades en Base)
from app.database import Base, engine
from app.errores import registrar_manejadores
from app.routers import asistentes, catalogo, clientes, eventos, reportes, staff

CARPETA_SQL = Path(__file__).parent / "sql"
SCRIPTS_AL_INICIAR = ["01_logica_eventos.sql", "02_reportes.sql", "03_catalogo.sql"]


def aplicar_scripts_sql() -> None:
    """Ejecuta los scripts .sql completos con la conexión nativa de psycopg2."""
    conexion = engine.raw_connection()
    try:
        with conexion.cursor() as cursor:
            for nombre in SCRIPTS_AL_INICIAR:
                cursor.execute((CARPETA_SQL / nombre).read_text(encoding="utf-8"))
        conexion.commit()
    finally:
        conexion.close()


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    aplicar_scripts_sql()
    yield


app = FastAPI(
    title="NexoEventos API",
    description=(
        "Sistema de información del Centro de Convenciones Nexo. "
        "Las reglas de negocio (A1–A5) y los reportes (B1–B4) viven en PostgreSQL. "
        "Envíe el encabezado **X-Usuario** para que la auditoría registre quién hizo cada cambio."
    ),
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

registrar_manejadores(app)

app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(staff.router, prefix="/staff", tags=["Staff"])
app.include_router(catalogo.router_salones, prefix="/salones", tags=["Salones"])
app.include_router(catalogo.router_servicios, prefix="/servicios", tags=["Servicios"])
app.include_router(eventos.router, prefix="/eventos", tags=["Eventos"])
app.include_router(asistentes.router, prefix="/asistentes", tags=["Asistentes"])
app.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])


@app.get("/", tags=["General"])
def raiz():
    return {"mensaje": "NexoEventos API en línea", "docs": "/docs"}
