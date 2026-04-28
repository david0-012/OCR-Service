import os
import shutil
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.repository import crear_documento, actualizar_documento
from app.services.ocr_service import extraer_texto
from app.services.procesamiento_service import procesar_texto

settings = get_settings()
logger = get_logger(__name__)


def procesar_documento(db: Session, archivo_temp: str, nombre_original: str) -> dict:
    """
    Orquesta el flujo completo de procesamiento de un documento.
    
    Pasos:
    1. Guarda el archivo en tmp/uploads
    2. Ejecuta OCR
    3. Procesa texto
    4. Persiste en BD
    5. Retorna resultado
    """
    documento_id = None
    ruta_destino = None
    
    try:
        logger.info(f"Iniciando procesamiento | archivo={nombre_original}")
        
        # Paso 1: Crear registro en BD
        documento = crear_documento(db, nombre_archivo="", nombre_original=nombre_original)
        documento_id = documento.id
        logger.info(f"Documento creado en BD | id={documento_id}")
        
        # Generar nombre único para el archivo
        extension = os.path.splitext(nombre_original)[-1]
        nombre_archivo_guardado = f"doc_{documento_id}{extension}"
        ruta_destino = os.path.join(settings.UPLOAD_DIR, nombre_archivo_guardado)
        
        # Asegurarse de que el directorio existe
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        # Mover archivo del temporal a la ubicación final
        shutil.move(archivo_temp, ruta_destino)
        logger.info(f"Archivo guardado | ruta={ruta_destino}")
        
        # Actualizar referencia en BD
        actualizar_documento(db, documento_id, nombre_archivo=nombre_archivo_guardado)
        
        # Paso 2: Ejecutar OCR
        try:
            texto_extraido = extraer_texto(ruta_destino)
            logger.info(f"OCR completado | caracteres={len(texto_extraido)}")
        except Exception as e:
            logger.error(f"Error en OCR | error={str(e)}")
            actualizar_documento(db, documento_id, estado="error")
            raise
        
        # Paso 3: Procesar texto
        try:
            datos_procesados = procesar_texto(texto_extraido)
            logger.info(f"Procesamiento completado | datos={datos_procesados}")
        except Exception as e:
            logger.error(f"Error en procesamiento | error={str(e)}")
            actualizar_documento(db, documento_id, estado="error")
            raise
        
        # Paso 4: Persistir en BD
        actualizar_documento(
            db,
            documento_id,
            texto_extraido=texto_extraido,
            datos_procesados=datos_procesados,
            estado="procesado"
        )
        
        logger.info(f"Documento procesado exitosamente | id={documento_id}")
        
        # Paso 5: Retornar resultado
        return {
            "id": documento_id,
            "nombre_archivo": nombre_archivo_guardado,
            "estado": "procesado",
            "resumen": datos_procesados,
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento de documento | error={str(e)}")
        if documento_id:
            actualizar_documento(db, documento_id, estado="error")
        # Limpiar archivos temporales/finales si existe alguno
        for ruta in (archivo_temp, ruta_destino):
            if ruta and os.path.exists(ruta):
                try:
                    os.remove(ruta)
                except OSError:
                    logger.warning(f"No se pudo eliminar archivo temporal | ruta={ruta}")
        raise
