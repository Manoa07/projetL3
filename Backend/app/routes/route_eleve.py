from typing import List

from fastapi import APIRouter

from DB.database import db_dependancy
from schema.sch_eleve import Create_eleve , Reponse_eleve ,Id_eleve
from services.eleve_service import create_eleve,get_eleve,get_eleve_id
router= APIRouter(prefix="/eleve",tags=["Eleves"])

@router.post("/create")
def create_eleve_route(eleve : Create_eleve , db: db_dependancy):
    return create_eleve(eleve,db)


@router.get("/all",response_model=List[Reponse_eleve])
def get_eleves_route(db:db_dependancy):
    return get_eleve(db)


@router.get("/numero/{eleve_numero}",response_model=Id_eleve)
def get_eleve_id_route(eleve_numero: int, db:db_dependancy):
    return get_eleve_id(eleve_numero,db)
