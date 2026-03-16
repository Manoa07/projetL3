from typing import List

from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_cours import Create_cours, Reponse_cours 
from models.cours import Cours
router= APIRouter(prefix="/cours",tags=["Cours"])

@router.post("/")
def create_cours(cours: Create_cours, db:db_dependancy):
    new_cours = Cours(
        Nom_cours = cours.Nom_cours,
        Professeur_cours= cours.Prof_cours,
        Date_cours=cours.Date_cours,
        Salle_cours=cours.Salle_cours
        )
    db.add(new_cours)
    db.commit()
    db.refresh(new_cours)
    return new_cours

@router.get("/",response_model=List[Reponse_cours])
def get_cours(db:db_dependancy):
    cours_res = db.query(Cours).all()
    return cours_res
