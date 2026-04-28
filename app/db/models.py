from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Documento(Base):
    __tablename__ = "documentos"
    __table_args__ = (
        CheckConstraint("estado IN ('pendiente', 'procesado', 'error')", name="ck_documentos_estado"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    nombre_original = Column(String(255), nullable=False)
    estado = Column(String(20), default="pendiente")  # pendiente | procesado | error
    texto_extraido = Column(Text, nullable=True)
    datos_procesados = Column(JSONB, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))