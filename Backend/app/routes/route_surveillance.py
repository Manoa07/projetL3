from typing import List
from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_surveillance import Create_surveillance , Eleve_surveillee
from models.surveillance import Surveillance
router= APIRouter(prefix="/surveillance",tags=["Surveillance"])

@router.post("/create")
def create_surveillance(surveillance:Create_surveillance,db : db_dependancy):
    new_surveillance=Surveillance(
        id_examen=surveillance.id_examen,
        id_eleve=surveillance.id_eleve,
        Status_examen=surveillance.Status_examen,
        Remarque=surveillance.Remarque
    )
    db.add(new_surveillance)
    db.commit()
    db.refresh(new_surveillance)
    return new_surveillance

@router.get("/eleve/{id_eleve}", response_model=List[Eleve_surveillee])
def voir_eleve(id_eleve:int ,db : db_dependancy):
    eleve=db.query(Surveillance).filter(Surveillance.id_eleve==id_eleve).all()
    return eleve
