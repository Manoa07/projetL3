import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.detection import Detection
from models.examen import Examen
from models.image_capture import ImageCapture
from models.surveillance_examen import SurveillanceExamen
from schema.sch_surveillance_examen import SurveillanceExamenCreate


logger = logging.getLogger(__name__)


def get_surveillance_examen(db: Session, surveillance_id: int):
    value = db.query(SurveillanceExamen).filter(
        SurveillanceExamen.id_surveillance == surveillance_id
    ).first()
    if not value:
        raise HTTPException(status_code=404, detail="Surveillance d'examen introuvable")
    return value


def get_all_surveillances_examen(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SurveillanceExamen).offset(skip).limit(limit).all()


def _validate_references(db: Session, data: SurveillanceExamenCreate):
    if not db.query(Examen).filter(Examen.id_examen == data.id_examen_examen).first():
        raise HTTPException(status_code=404, detail="Examen introuvable")
    if data.id_capture_capture is not None and not db.query(ImageCapture).filter(
        ImageCapture.id_capture == data.id_capture_capture
    ).first():
        raise HTTPException(status_code=404, detail="Capture introuvable")
    if data.id_detection_detection is not None and not db.query(Detection).filter(
        Detection.id_detection == data.id_detection_detection
    ).first():
        raise HTTPException(status_code=404, detail="Détection introuvable")


def create_surveillance_examen(db: Session, data: SurveillanceExamenCreate):
    _validate_references(db, data)
    value = SurveillanceExamen(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la surveillance d'examen", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la surveillance d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_surveillance_examen(db: Session, surveillance_id: int, data: SurveillanceExamenCreate):
    _validate_references(db, data)
    value = get_surveillance_examen(db, surveillance_id)
    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la surveillance d'examen", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la surveillance d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_surveillance_examen(db: Session, surveillance_id: int):
    value = get_surveillance_examen(db, surveillance_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la surveillance d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
