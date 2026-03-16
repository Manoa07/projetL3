from fastapi import Depends,APIRouter
from sqlalchemy.orm import Session
from DB.database import db_dependancy
from schema.sch_eleve import Create_eleve , Reponse_eleve ,Id_eleve
from models.eleve import Eleve
router= APIRouter(prefix="/eleve",tags=["Eleves"])

@router.post("/")
def create_eleve(eleve: Create_eleve, db:db_dependancy):
    new_eleve = Eleve(
        Nom_eleve = eleve.Nom,
        Prenom_eleve= eleve.Prenom,
        Classe_eleve= eleve.Classe,
        Numero= eleve.Numero
        )
    db.add(new_eleve)
    db.commit()
    db.refresh(new_eleve)
    return new_eleve


@router.get("/")
def get_eleves(db:db_dependancy):
    eleve_res = db.query(Eleve).all()
    return eleve_res


@router.get("/{eleve_id}")
def get_eleve(eleve_id: int, db:db_dependancy):
    eleve= db.query(Eleve).filter(Eleve.Id_eleve == eleve_id).first