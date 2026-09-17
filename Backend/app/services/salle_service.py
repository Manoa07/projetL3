import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.salle import Salle
from schema.sch_salle import SalleCreate


logger = logging.getLogger(__name__)


def get_salle(db: Session, salle_id: int):
    value = db.query(Salle).filter(Salle.id_salle == salle_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Salle introuvable")
    return value


def get_all_salles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Salle).order_by(Salle.nom_salle).offset(skip).limit(limit).all()


def create_salle(db: Session, data: SalleCreate):
    if db.query(Salle).filter(Salle.nom_salle == data.nom_salle.strip()).first():
        raise HTTPException(status_code=409, detail="Salle déjà existante")
    value = Salle(nom_salle=data.nom_salle.strip())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la salle", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la salle", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_salle(db: Session, salle_id: int, data: SalleCreate):
    value = get_salle(db, salle_id)
    name = data.nom_salle.strip()
    duplicate = db.query(Salle).filter(
        Salle.nom_salle == name,
        Salle.id_salle != salle_id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Salle déjà existante")

    value.nom_salle = name
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la salle", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la salle", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_salle(db: Session, salle_id: int):
    value = get_salle(db, salle_id)
    try:
        db.delete(value)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        logger.error("Salle référencée lors de la suppression", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="La salle est utilisée par un cours ou un examen.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la salle", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
