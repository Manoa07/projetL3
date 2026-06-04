from typing import List

from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_examen import Create_examen, Voir_examens
from services.examen_service import create_examen,get_examen
router= APIRouter(prefix="/examen",tags=["Examen"])

@router.post("/create")
def create_examen_route(examen : Create_examen , db : db_dependancy):
    return create_examen(examen , db)

@router.get("/cours/{id_cours}", response_model=List[Voir_examens])
def get_examen_route(id_cours:int,db:db_dependancy):
    return get_examen(id_cours,db)
