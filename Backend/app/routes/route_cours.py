from typing import List

from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_cours import Create_cours, Reponse_cours 
from services.cours_service import create_cours, get_cours
router= APIRouter(prefix="/cours",tags=["Cours"])

@router.post("/create")
def create_cours_route(cours: Create_cours, db:db_dependancy):
    return create_cours(cours,db)

@router.get("/all",response_model=List[Reponse_cours])
def get_cours_all(db:db_dependancy):
    return get_cours(db)
