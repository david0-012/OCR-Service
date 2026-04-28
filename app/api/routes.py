import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.db.repository import obtener_documento, listar_documentos
from app.schemas.documento import DocumentoResponse, DocumentoListResponse, DocumentoUploadResponse
from app.services.documento_service import procesar_documento

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.post("", response_model=DocumentoUploadResponse, status_code=201)
async def subir_documento(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Sube y procesa un archivo (PDF o imagen).
    
    - **file**: Archivo a procesar (PDF o imagen)
    
    Retorna:
    - id: ID del documento en BD
    - nombre_archivo: Nombre guardado
    - estado: Estado del procesamiento
    - resumen: Datos procesados (num_palabras, tipo_detectado)
    """
    logger.info(f"Solicitud de subida | archivo={file.filename} | size={file.size}")
    
    # Validar tamaño
    if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        logger.warning(f"Archivo demasiado grande | tamaño={file.size}")
        raise HTTPException(
            status_code=400,
            detail=f"El archivo no puede superar {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Validar extensión
    extension = Path(file.filename).suffix.lower()
    extensiones_permitidas = {".pdf", ".jpg", ".jpeg", ".png"}
    if extension not in extensiones_permitidas:
        logger.warning(f"Extensión no permitida | extensión={extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Extensión no permitida. Permitidas: {', '.join(extensiones_permitidas)}"
        )
    
    # Guardar temporalmente
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
            contenido = await file.read()
            tmp.write(contenido)
            temp_path = tmp.name
        
        logger.info(f"Archivo guardado temporalmente | temp_path={temp_path}")
        
        # Procesar documento
        resultado = procesar_documento(db, temp_path, file.filename)
        
        logger.info(f"Documento subido y procesado | id={resultado['id']}")
        
        # Obtener documento actualizado de BD
        documento = obtener_documento(db, resultado['id'])
        if not documento:
            logger.error(f"Documento no encontrado despues del procesamiento | id={resultado['id']}")
            raise HTTPException(
                status_code=500,
                detail="No fue posible recuperar el documento procesado"
            )
        
        return DocumentoUploadResponse(
            id=documento.id,
            nombre_archivo=documento.nombre_archivo,
            estado=documento.estado,
            resumen=resultado.get("resumen"),
            fecha_creacion=documento.fecha_creacion,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en subida de documento | error={str(e)}")
        error_text = str(e)
        if "Falta configurar AZURE_ENDPOINT" in error_text:
            raise HTTPException(
                status_code=400,
                detail=error_text,
            )
        if "Access denied due to invalid subscription key" in error_text:
            raise HTTPException(
                status_code=502,
                detail="Azure rechazó la autenticación o el endpoint no corresponde al recurso configurado.",
            )
        if "Azure rechazó la autenticación" in error_text:
            raise HTTPException(
                status_code=502,
                detail=error_text,
            )
        raise HTTPException(
            status_code=500,
            detail="Error procesando el documento"
        )
    finally:
        # Limpiar temporal
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.get("/{documento_id}", response_model=DocumentoResponse)
async def obtener_info_documento(
    documento_id: int,
    db: Session = Depends(get_db),
):
    """
    Obtiene información detallada de un documento procesado.
    
    - **documento_id**: ID del documento
    
    Retorna:
    - id, nombre_archivo, estado
    - texto_extraido: Texto obtenido por OCR
    - datos_procesados: Análisis (num_palabras, tipo_detectado)
    - fecha_creacion: Fecha de creación
    """
    logger.info(f"Solicitud de consulta | documento_id={documento_id}")
    
    documento = obtener_documento(db, documento_id)
    
    if not documento:
        logger.warning(f"Documento no encontrado | documento_id={documento_id}")
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return DocumentoResponse.model_validate(documento)


@router.get("", response_model=list[DocumentoListResponse])
async def listar_mis_documentos(
    db: Session = Depends(get_db),
):
    """
    Lista todos los documentos procesados (sin paginación).
    """
    logger.info("Solicitud de listado de todos los documentos")

    documentos = listar_documentos(db)

    return [DocumentoListResponse.model_validate(doc) for doc in documentos]
