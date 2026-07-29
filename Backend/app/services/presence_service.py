from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.presence import Presence

def create_presence(presence,db):
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
            print(e)
    else:
        raise HTTPException(
            status_code=409,
            detail="presence existant"
        )
def get_presence_all(eleve_id,db):
    eleve_verifie=db.query(Presence).filter(Presence.id_eleve==eleve_id).all()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="aucune presence sur cette eleve"
        )
    return eleve_verifie
def get_presence(eleve_id,db):
    eleve_verifie=db.query(Presence).filter(Presence.id_eleve==eleve_id).first()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="eleve non trouvé"
        )
    return eleve_verifie
