from typing import List

from fastapi import Depends,APIRouter

from DB.database import db_dependancy
from schema.sch_presence import Create_presence , Reponse_presence ,Presence_eleve
from models.presence import Presence
router= APIRouter(prefix="/presence",tags=["Presence"])

@router.post("/")
def create_presence(presence: Create_presence, db:db_dependancy):
    new_presence= Presence(
        id_cours=presence.id_cours,
        id_eleve=presence.id_eleve,
        Status_presence=presence.Status_presence,
        Heure_presence=presence.Heure_presence,
        Date_presence=presence.Date_presence
        )
    db.add(new_presence)
    db.commit()
    db.refresh(new_presence)
    return new_presence

@router.get("/eleve/{eleve_id}",response_model=List[Presence_eleve])
def get_presence(eleve_id :int,db:db_dependancy):
    eleve=db.query(Presence).filter(Presence.id_eleve==eleve_id).all()
    return eleve
@router.get("/eleve_last/{eleve_id}",response_model=Presence_eleve)
def get_presence(eleve_id :int,db:db_dependancy):
    eleve=db.query(Presence).filter(Presence.id_eleve==eleve_id).first()
    return eleve
