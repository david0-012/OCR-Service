# OCR Service

Servicio de OCR y procesamiento de documentos usando **Python** **FastAPI**, **Azure Document Intelligence** y **PostgreSQL**.

## Documentación

En la carpeta `docs/` encontrarás:

- [Diseño conceptual de arquitectura en Azure](docs/diseño_conceptual_arquitectura_azure.jpeg)
- [Script de creación de esquema y tabla de base de datos PostgreSQL](docs/script_creacion_esquema_tabla_bd.sql)
- [Explicación de arquitectura](docs/documentacion.md)

---

## Requisitos

- Python 3.13+
- Docker
- Azure Document Intelligence (API Key + Endpoint)

---

## Instalación de uv

`uv` es un gestor de paquetes rápido para Python.

**Opción 1: Con pip (recomendado para comenzar)**

```bash
pip install uv
```

**Opción 2: Script**

**Windows (PowerShell)**:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verifica la instalación:
```bash
uv --version
```

---

## Instalación y Ejecución

### Paso 1: Sincronizar dependencias y crear entorno virtual

```bash
uv sync
```

Esto creará automáticamente el entorno virtual `.venv` e instalará las dependencias.

---

### Paso 2: Activar el entorno virtual

**Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

---

### Paso 3: Configuración del entorno

Toma de ejemplo [`.env.example`](.env.example) para crear `.env` y completa las variables:

```env
DATABASE_URL=postgresql://usuario:contraseña@servidor:puerto/base_datos
APP_NAME=OCR Service
APP_VERSION=1.0.0
DEBUG=False
UPLOAD_DIR=tmp/uploads
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
AZURE_API_KEY=api_key
AZURE_ENDPOINT=endpoint
```

**Para obtener Azure credenciales**:
1. Crea un recurso "Document Intelligence" en Azure Portal
2. Ve a "Claves y punto de conexión"
3. Copia la API Key (Clave 1 o 2) y Endpoint (Extremo) en `.env`

---

### Paso 4: Levantar base de datos PostgreSQL con Docker

Ejecuta en la terminal:
```bash
docker-compose up -d
```

---

### Paso 5: Ejecutar la aplicación

Ejecuta en la terminal:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API

API: http://localhost:8000  
Docs: http://localhost:8000/docs

### Endpoints diponibles

- **POST** /documentos - Cargar documento para realizar OCR

- **GET** /documentos/{id} - Obtener documento detallado con resultados de OCR

- **GET** /documentos - Listar documentos almacenados en la base de datos
