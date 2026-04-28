from sqlalchemy.orm import Session
from app.db.models import Documento


def crear_documento(db: Session, nombre_archivo: str, nombre_original: str) -> Documento:
    documento = Documento(
        nombre_archivo=nombre_archivo,
        nombre_original=nombre_original,
        estado="pendiente",
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento


def actualizar_documento(db: Session, documento_id: int, **kwargs) -> Documento | None:
    documento = db.query(Documento).filter(Documento.id == documento_id).first()
    if not documento:
        return None
    for key, value in kwargs.items():
        setattr(documento, key, value)
    db.commit()
    db.refresh(documento)
    return documento


def obtener_documento(db: Session, documento_id: int) -> Documento | None:
    return db.query(Documento).filter(Documento.id == documento_id).first()


def listar_documentos(db: Session, skip: int = 0, limit: int = 100) -> list[Documento]:
    return db.query(Documento).offset(skip).limit(limit).all()