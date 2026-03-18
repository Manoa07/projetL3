from typing import List

from fastapi import APIRouter

from DB.database import db_dependancy
from schema.sch_eleve import Create_eleve , Reponse_eleve ,Id_eleve
from models.eleve import Eleve
router= APIRouter(prefix="/eleve",tags=["Eleves"])

@router.post("/create")
def create_eleve(eleve: Create_eleve, db:db_dependancy):
    new_eleve = Eleve(
        Nom_eleve = eleve.Nom_eleve,
        Prenom_eleve= eleve.Prenom_eleve,
        Classe_eleve= eleve.Classe_eleve,
        Numero_eleve= eleve.Numero_eleve
        )
    db.add(new_eleve)
    db.commit()
    db.refresh(new_eleve)
    return new_eleve


@router.get("/all",response_model=List[Reponse_eleve])
def get_eleves(db:db_dependancy):
    eleve_res = db.query(Eleve).all()
    return eleve_res


@router.get("/numero/{eleve_numero}",response_model=Id_eleve)
def get_eleve_id(eleve_numero: int, db:db_dependancy):
    eleve= db.query(Eleve).filter(Eleve.Numero_eleve == eleve_numero).first()
    return eleve
