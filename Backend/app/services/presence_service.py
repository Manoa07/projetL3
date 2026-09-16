import logging

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models.cours import Cours
from models.eleve import Eleve
from models.presence import Presence


logger = logging.getLogger(__name__)

def create_presence(presence,db):
    eleve = db.query(Eleve).filter(Eleve.Id_eleve == presence.id_eleve).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    cours = db.query(Cours).filter(Cours.Id_cours == presence.id_cours).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    presence_verifie=db.query(Presence).filter(
        and_(
            Presence.id_eleve==presence.id_eleve,
            Presence.id_cours==presence.id_cours,
            Presence.Date_presence==presence.Date_presence
            )
        ).first()
    if not presence_verifie:   
        new_presence= Presence(
            id_cours=presence.id_cours,
            id_eleve=presence.id_eleve,
            Status_presence=presence.Status_presence,
            Heure_presence=presence.Heure_presence,
            Date_presence=presence.Date_presence
        )
        try:
            db.add(new_presence)
            db.commit()
            db.refresh(new_presence)
            return new_presence
        except IntegrityError as e:
            db.rollback()
            logger.error("Erreur d'intégrité lors de la création de la présence", exc_info=e)
            raise HTTPException(
                status_code=409,
                detail="La présence n'a pas pu être enregistrée.",
            ) from e
        except Exception as e:
            db.rollback()
            logger.error("Erreur lors de la création de la présence", exc_info=e)
            raise HTTPException(
                status_code=500,
                detail="Erreur interne lors de la création de la présence.",
            ) from e
    else:
        raise HTTPException(
            status_code=409,
            detail="presence existant"
        )
def get_presence_all(eleve_id, db):
    return db.query(Presence).filter(Presence.id_eleve == eleve_id).all()  # [] si vide

def get_presence(eleve_id, db):
    eleve_verifie = db.query(Presence).filter(Presence.id_eleve == eleve_id).first()
    if not eleve_verifie:
        raise HTTPException(status_code=404, detail="eleve non trouvé")
    return eleve_verifie
