import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.eleve import Eleve
from models.examen import Examen
from models.presence_examen import PresenceExamen
from schema.sch_presence_examen import PresenceExamenCreate


logger = logging.getLogger(__name__)


def get_presence_examen(db: Session, presence_id: int):
    value = db.query(PresenceExamen).filter(
        PresenceExamen.id_presence_examen == presence_id
    ).first()
    if not value:
        raise HTTPException(status_code=404, detail="Présence d'examen introuvable")
    return value


def get_all_presence_examens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PresenceExamen).offset(skip).limit(limit).all()


def create_presence_examen(db: Session, data: PresenceExamenCreate):
    if not db.query(Eleve).filter(Eleve.Id_eleve == data.id_eleve_eleve).first():
        raise HTTPException(status_code=404, detail="Élève introuvable")
    if not db.query(Examen).filter(Examen.id_examen == data.id_examen_examen).first():
        raise HTTPException(status_code=404, detail="Examen introuvable")
    duplicate = db.query(PresenceExamen).filter(
        PresenceExamen.id_eleve_eleve == data.id_eleve_eleve,
        PresenceExamen.id_examen_examen == data.id_examen_examen,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Présence d'examen déjà existante")
    value = PresenceExamen(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la présence d'examen", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la présence d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_presence_examen(db: Session, presence_id: int, data: PresenceExamenCreate):
    value = get_presence_examen(db, presence_id)
    if not db.query(Eleve).filter(Eleve.Id_eleve == data.id_eleve_eleve).first():
        raise HTTPException(status_code=404, detail="Élève introuvable")
    if not db.query(Examen).filter(Examen.id_examen == data.id_examen_examen).first():
        raise HTTPException(status_code=404, detail="Examen introuvable")
    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la présence d'examen", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la présence d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_presence_examen(db: Session, presence_id: int):
    value = get_presence_examen(db, presence_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la présence d'examen", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
