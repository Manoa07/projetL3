import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.matiere import Matiere
from models.professeur import Professeur
from models.salle import Salle


logger = logging.getLogger(__name__)


def get_all_professeurs(db: Session):
    return db.query(Professeur).order_by(Professeur.nom_professeur).all()


def create_professeur(db: Session, data):
    value = Professeur(**data.model_dump())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création du professeur", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données.") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création du professeur", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne.") from error


def get_all_salles(db: Session):
    return db.query(Salle).order_by(Salle.nom_salle).all()


def create_salle(db: Session, data):
    value = Salle(nom_salle=data.nom.strip())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la salle", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données.") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la salle", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne.") from error


def get_all_matieres(db: Session):
    return db.query(Matiere).order_by(Matiere.nom_matiere).all()


def create_matiere(db: Session, data):
    value = Matiere(nom_matiere=data.nom.strip())
    try:
        db.add(value)
        db.commit()
        db.refresh(value)
        return value
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la matière", exc_info=error)
        raise HTTPException(status_code=409, detail="Conflit de données.") from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la création de la matière", exc_info=error)
        raise HTTPException(status_code=500, detail="Erreur interne.") from error