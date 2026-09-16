import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.matiere import Matiere
from schema.sch_matiere import MatiereCreate


logger = logging.getLogger(__name__)


def get_matiere(db: Session, matiere_id: int):
    value = db.query(Matiere).filter(Matiere.id_matiere == matiere_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Matière introuvable")
    return value


def get_all_matieres(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Matiere).order_by(Matiere.nom_matiere).offset(skip).limit(limit).all()


def create_matiere(db: Session, data: MatiereCreate):
    name = data.nom_matiere.strip()
    if db.query(Matiere).filter(Matiere.nom_matiere == name).first():
        raise HTTPException(status_code=409, detail="Matière déjà existante")
    value = Matiere(nom_matiere=name)
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la matière", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la matière", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_matiere(db: Session, matiere_id: int, data: MatiereCreate):
    value = get_matiere(db, matiere_id)
    value.nom_matiere = data.nom_matiere.strip()
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de la matière", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de la matière", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_matiere(db: Session, matiere_id: int):
    value = get_matiere(db, matiere_id)
    try:
        db.delete(value)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de la matière", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
