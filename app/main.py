from contextlib import asynccontextmanager
from asyncio import sleep
from time import perf_counter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.models import Base
from app.api.routes import router as documentos_router

settings = get_settings()


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]

# Configurar logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la aplicación."""
    # STARTUP
    max_reintentos = 10
    for intento in range(1, max_reintentos + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Tablas de BD verificadas/creadas exitosamente")
            break
        except Exception as e:
            if intento == max_reintentos:
                logger.error(f"Error inicializando BD tras {max_reintentos} intentos | error={str(e)}")
                raise
            logger.warning(
                f"BD no disponible, reintentando ({intento}/{max_reintentos}) | error={str(e)}"
            )
            await sleep(2)
    
    yield  # La app corre y recibe requests
    
    # SHUTDOWN
    logger.info("Cerrando aplicación")


# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Servicio de OCR y procesamiento de documentos",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(documentos_router)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start_time = perf_counter()
    response = await call_next(request)
    duration_ms = (perf_counter() - start_time) * 1000
    logger.info(
        f"Request | method={request.method} | path={request.url.path} | status={response.status_code} | duration_ms={duration_ms:.2f}"
    )
    return response


@app.get("/")
async def root():
    """Endpoint de prueba."""
    return {
        "servicio": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "activo",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {
        "estado": "ok",
        "servicio": settings.APP_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
