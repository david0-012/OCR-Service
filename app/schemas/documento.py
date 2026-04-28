from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Literal, Any


class ResumenProcesamiento(BaseModel):
    num_palabras: int
    tipo_detectado: str


class DocumentoResponse(BaseModel):
    id: int
    nombre_archivo: str
    nombre_original: str
    estado: Literal["pendiente", "procesado", "error"]
    texto_extraido: Optional[str] = None
    datos_procesados: Optional[dict[str, Any]] = None
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentoListResponse(BaseModel):
    id: int
    nombre_archivo: str
    nombre_original: str
    estado: Literal["pendiente", "procesado", "error"]
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentoUploadResponse(BaseModel):
    id: int
    nombre_archivo: str
    estado: Literal["pendiente", "procesado", "error"]
    resumen: Optional[ResumenProcesamiento] = None
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
