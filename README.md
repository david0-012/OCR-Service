# OCR Service

Servicio de OCR y procesamiento de documentos usando **FastAPI**, **Azure Document Intelligence** y **PostgreSQL**.

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

`uv` es un gestor de paquetes rápido para Python. Instálalo así:

**Opción 1: Script**

**Windows (PowerShell)**:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Opción 2: Con pip**

```bash
pip install uv
```

Verifica la instalación:
```bash
uv --version
```

---

## Instalación y Ejecución

### Opción 1: Con `uv` (recomendado)

```bash
# Sincronizar dependencias (crea .venv automáticamente)
uv sync

# Ejecutar la aplicación
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Con `pip`

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Configuración

Toma de ejemplo `.env.example` para crear `.env` y completa las variables:

```env
# URL de conexión a la base de datos PostgreSQL.
DATABASE_URL=postgresql://usuario:contraseña@servidor:puerto/base_datos

# Nombre de la aplicación
APP_NAME=OCR Service

# Versión de la aplicación
APP_VERSION=1.0.0

# Modo debug (true/false). Usar false en producción.
DEBUG=False

# Directorio donde se guardan los archivos subidos
UPLOAD_DIR=tmp/uploads

# Tamaño máximo permitido por archivo (en MB)
MAX_FILE_SIZE_MB=10

# Orígenes permitidos para CORS (separados por comas)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Clave API de Azure (para OCR o servicios cognitivos)
AZURE_API_KEY=api_key

# Endpoint de Azure para el servicio correspondiente
AZURE_ENDPOINT=endpoint
```

**Para obtener Azure credenciales**:
1. Crea un recurso "Document Intelligence" en Azure Portal
2. Ve a "Claves y punto de conexión"
3. Copia la API Key (Clave 1 o 2) y Endpoint (Extremo) en `.env`

### PostgreSQL

Ejecutar compose para levantar el servicio de base de datos PostgreSQL:

```bash
docker-compose up -d
```

---

## API

API: **http://localhost:8000**  
Docs: **http://localhost:8000/docs**

### Endpoints

**POST** `/documentos` - Subir archivo

**GET** `/documentos/{id}` - Obtener documento detallado

**GET** `/documentos` - Listar documentos

---
