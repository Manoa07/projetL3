from typing import List

from fastapi import APIRouter
from datetime import datetime
from DB.database import db_dependancy
from schema.sch_examen import Create_examen, Voir_examens
from models.examen import Examen
router= APIRouter(prefix="/examen",tags=["Examen"])

@router.post("/create")
def create_examen(examen : Create_examen , db : db_dependancy):
    new_examen =Examen(
        id_cours=examen.id_cours,
        date_examen=examen.date_examen,
        Heure_debut=examen.heure_debut,
        Heure_fin=examen.heure_fin,
        Salle_examen=examen.salle_examen
    )
    db.add(new_examen)
    db.commit()
    db.refresh(new_examen)
    return new_examen
@router.get("/cours/{id_cours}", response_model=Voir_examens)
def get_examen(id_cours:int,db:db_dependancy):
    reponse=db.query(Examen).filter(Examen.id_cours==id_cours).all()
    return reponse
