from typing import List

from fastapi import APIRouter, status
from DB.database import db_dependancy
from schema.sch_cours import Create_cours, Reponse_cours 
from services import cours_service
from services.cours_service import create_cours, get_cours
router= APIRouter(prefix="/cours",tags=["Cours"])

@router.post("/create")
def create_cours_route(cours: Create_cours, db:db_dependancy):
    return create_cours(cours,db)

@router.get("/all",response_model=List[Reponse_cours])
def get_cours_all(db:db_dependancy):
    return get_cours(db)


@router.put("/{cours_id}", response_model=Reponse_cours)
def update_cours_route(
    cours_id: int,
    data: Create_cours,
    db: db_dependancy,
):
    return cours_service.update_cours(db, cours_id, data)


@router.delete("/{cours_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cours_route(cours_id: int, db: db_dependancy):
    cours_service.delete_cours(db, cours_id)
    return None
