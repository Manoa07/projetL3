import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.detection import Detection
from models.eleve import Eleve
from models.image_capture import ImageCapture
from schema.sch_detection import DetectionCreate


logger = logging.getLogger(__name__)


def get_detection(db: Session, detection_id: int):
    value = db.query(Detection).filter(Detection.id_detection == detection_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Détection introuvable")
    return value


def get_all_detections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Detection).order_by(Detection.id_detection).offset(skip).limit(limit).all()


def create_detection(db: Session, data: DetectionCreate):
    if not db.query(ImageCapture).filter(
        ImageCapture.id_capture == data.id_capture_capture
    ).first():
        raise HTTPException(status_code=404, detail="Capture introuvable")
    if not db.query(Eleve).filter(
        Eleve.Id_eleve == data.id_eleve_eleve
    ).first():
        raise HTTPException(status_code=404, detail="Élève introuvable")
    duplicate = db.query(Detection).filter(
        Detection.id_capture_capture == data.id_capture_capture,
        Detection.id_eleve_eleve == data.id_eleve_eleve,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Détection déjà existante")
    value = Detection(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la détection", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la détection", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_detection(db: Session, detection_id: int, data: DetectionCreate):
    value = get_detection(db, detection_id)
    if not db.query(ImageCapture).filter(
        ImageCapture.id_capture == data.id_capture_capture
    ).first():
        raise HTTPException(status_code=404, detail="Capture introuvable")
    if not db.query(Eleve).filter(
        Eleve.Id_eleve == data.id_eleve_eleve
    ).first():
        raise HTTPException(status_code=404, detail="Élève introuvable")
    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la détection", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la détection", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_detection(db: Session, detection_id: int):
    value = get_detection(db, detection_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la détection", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
