import logging
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.image_capture import ImageCapture
from schema.sch_image_capture import ImageCaptureCreate


logger = logging.getLogger(__name__)


def _validate_capture_path(file_path: str):
    path = Path(file_path)
    if path.is_absolute() or ".." in path.parts:
        raise HTTPException(status_code=422, detail="Chemin de capture invalide")


def get_image_capture(db: Session, capture_id: int):
    value = db.query(ImageCapture).filter(ImageCapture.id_capture == capture_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Capture introuvable")
    return value


def get_all_image_captures(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ImageCapture).order_by(ImageCapture.id_capture).offset(skip).limit(limit).all()


def create_image_capture(db: Session, data: ImageCaptureCreate):
    _validate_capture_path(data.fichier_capture)
    value = ImageCapture(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la capture", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la capture", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_image_capture(db: Session, capture_id: int, data: ImageCaptureCreate):
    _validate_capture_path(data.fichier_capture)
    value = get_image_capture(db, capture_id)
    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la capture", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la capture", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_image_capture(db: Session, capture_id: int):
    value = get_image_capture(db, capture_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la capture", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
