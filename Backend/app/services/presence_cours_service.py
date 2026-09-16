import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.cours import Cours
from models.eleve import Eleve
from models.presence_cours import PresenceCours
from schema.sch_presence_cours import PresenceCoursCreate


logger = logging.getLogger(__name__)


def get_presence_cours(db: Session, presence_id: int):
    value = db.query(PresenceCours).filter(
        PresenceCours.id_presence_cours == presence_id
    ).first()
    if not value:
        raise HTTPException(status_code=404, detail="Présence de cours introuvable")
    return value


def get_all_presence_cours(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PresenceCours).offset(skip).limit(limit).all()


def create_presence_cours(db: Session, data: PresenceCoursCreate):
    if not db.query(Cours).filter(Cours.Id_cours == data.id_cours_cours).first():
        raise HTTPException(status_code=404, detail="Cours introuvable")
    if not db.query(Eleve).filter(Eleve.Id_eleve == data.id_eleve_eleve).first():
        raise HTTPException(status_code=404, detail="Élève introuvable")
    duplicate = db.query(PresenceCours).filter(
        PresenceCours.id_cours_cours == data.id_cours_cours,
        PresenceCours.id_eleve_eleve == data.id_eleve_eleve,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Présence de cours déjà existante")
    value = PresenceCours(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la présence de cours", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la présence de cours", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_presence_cours(db: Session, presence_id: int, data: PresenceCoursCreate):
    value = get_presence_cours(db, presence_id)
    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la présence de cours", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la présence de cours", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_presence_cours(db: Session, presence_id: int):
    value = get_presence_cours(db, presence_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la présence de cours", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
