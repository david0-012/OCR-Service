## Documentación de Arquitectura

### Estructura de Carpetas y Componentes

#### Estructura del Proyecto

```
/
├── AGENTS.md
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── documento.py
│   └── services/
│       ├── __init__.py
│       ├── documento_service.py
│       ├── ocr_service.py
│       └── procesamiento_service.py
├── tmp/
│   └── uploads/
└── .env (no incluido en repo)
```

### Detalle de Carpetas y Componentes

#### /app — Código fuente principal
- `app/main.py` — Punto de entrada: configura FastAPI, CORS, lifespan (startup/shutdown), middleware de logging e incluye routers.

#### /app/api — Rutas HTTP / Endpoints
- `app/api/routes.py` — Endpoints REST principales:
  - `POST /documentos` — Subida y procesamiento de archivos.
  - `GET /documentos` — Listado de documentos en bd.
  - `GET /documentos/{id}` — Detalle de documento.
- Responsabilidad: validación básica, manejo de `UploadFile` temporal, gestión de errores HTTP y respuestas serializadas con Pydantic.

#### /app/services — Lógica de negocio y orquestación
- `app/services/documento_service.py` — Orquesta el flujo completo:
  - Crea el registro en BD (estado `pendiente`).
  - Mueve el archivo desde el temporal a `UPLOAD_DIR`.
  - Invoca OCR y procesamiento.
  - Actualiza estado y guarda resultado en BD.
- `app/services/ocr_service.py` — Abstracción del OCR: mock para desarrollo y adaptador Azure Document Intelligence para producción.
- `app/services/procesamiento_service.py` — Limpieza de texto, extracción de campos, conteo de palabras y clasificación de tipo de documento.

Diseño: separación clara entre orquestador (`documento_service`) y adaptadores (`ocr_service`, `procesamiento_service`) para facilitar sustituir proveedores.

#### /app/db — Persistencia y acceso a datos
- `app/db/models.py` — Definición ORM (tabla `documentos` con `texto_extraido`, `datos_procesados`, `estado`, etc.).
- `app/db/repository.py` — Operaciones CRUD encapsuladas (`crear_documento`, `actualizar_documento`, `obtener_documento`, `listar_documentos`).
- `app/db/session.py` — Configuración de `engine`, `SessionLocal` y `get_db()` (dependencia FastAPI). Usa `DATABASE_URL` desde configuración.

Observación: se usa `JSONB` para `datos_procesados` y `CheckConstraint` para restringir valores de `estado`.

#### /app/schemas — Esquemas Pydantic / Validación
- `app/schemas/documento.py` — Modelos de respuesta/serialización: `DocumentoResponse`, `DocumentoListResponse`, `DocumentoUploadResponse`.

#### /app/core — Configuración y logging
- `app/core/config.py` — Clase `Settings` con variables: `DATABASE_URL`, `AZURE_API_KEY`, `AZURE_ENDPOINT`, `UPLOAD_DIR`, `MAX_FILE_SIZE_MB`, `CORS_ORIGINS`, `DEBUG`. Carga desde `.env`.
- `app/core/logging.py` — Inicializa logging global y atenúa ruido de librerías externas.

#### /tmp/uploads — Almacenamiento de archivos subidos
- Directorio donde se mueven los archivos una vez creado el registro en BD. Configurable vía `UPLOAD_DIR`.

#### Infraestructura y dependencias
- `docker-compose.yml` — Levanta PostgreSQL (`postgres:15-alpine`) con variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y volumen persistente.
- `pyproject.toml` — Dependencias y configuración del proyecto.

---

### Flujo de procesamiento (resumen funcional)

1. Cliente envía `POST /documentos` con un archivo.
2. El router valida tamaño y extensión y guarda el archivo en un temporal.
3. Llama a `procesar_documento` en `documento_service`:
   - Crea registro en BD con estado `pendiente`.
   - Mueve archivo a `UPLOAD_DIR` (ej. `tmp/uploads/doc_{id}.pdf`).
   - Llama a `ocr_service.extraer_texto()` (mock o Azure).
   - Llama a `procesamiento_service.procesar_texto()` para extraer campos y clasificar.
   - Actualiza registro en BD con `texto_extraido`, `datos_procesados` y `estado=procesado` (o `error` si falla).
4. El router responde con `201 Created` y resumen del procesamiento.

---

### Capas de la Arquitectura

- Capa de Presentación (API Layer): `app/main.py` — Exponer endpoints, middleware y health checks.
- Capa de Negocio: `app/services/documento_service.py` y `app/services/procesamiento_service.py`.
- Capa de Integración/Adaptadores: `app/services/ocr_service.py` y `app/db/repository.py`.
- Capa de Datos: `app/db/models.py`, `app/db/session.py` y PostgreSQL (`docker-compose.yml`).
- Observabilidad y Configuración: `app/core/config.py`, `app/core/logging.py`.

---