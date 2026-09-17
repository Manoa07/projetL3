import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.professeur import Professeur
from schema.sch_professeur import ProfesseurCreate


logger = logging.getLogger(__name__)


def get_professeur(db: Session, professeur_id: int):
    value = db.query(Professeur).filter(Professeur.id_professeur == professeur_id).first()
    if not value:
        raise HTTPException(status_code=404, detail="Professeur introuvable")
    return value


def get_all_professeurs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Professeur).order_by(Professeur.nom_professeur).offset(skip).limit(limit).all()


def create_professeur(db: Session, data: ProfesseurCreate):
    duplicate = db.query(Professeur).filter(
        Professeur.matricule_professeur == data.matricule_professeur
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Professeur déjà existant")

    value = Professeur(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création du professeur", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création du professeur", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def update_professeur(db: Session, professeur_id: int, data: ProfesseurCreate):
    value = get_professeur(db, professeur_id)
    duplicate = db.query(Professeur).filter(
        Professeur.matricule_professeur == data.matricule_professeur,
        Professeur.id_professeur != professeur_id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Matricule déjà utilisé")

    for field, field_value in data.model_dump().items():
        setattr(value, field, field_value)
    try:
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour du professeur", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour du professeur", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error


def delete_professeur(db: Session, professeur_id: int):
    value = get_professeur(db, professeur_id)
    try:
        db.delete(value)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        logger.error("Professeur référencé lors de la suppression", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="Le professeur est utilisé par un cours.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression du professeur", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne") from error
