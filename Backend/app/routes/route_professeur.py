from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_professeur import ProfesseurCreate, ProfesseurResponse
from services import professeur_service


router = APIRouter(prefix="/professeur", tags=["Professeurs"])


@router.post("/create", response_model=ProfesseurResponse, status_code=status.HTTP_201_CREATED)
def create_professeur(data: ProfesseurCreate, db: db_dependancy):
    return professeur_service.create_professeur(db, data)


@router.get("/all", response_model=list[ProfesseurResponse])
def get_professeurs(db: db_dependancy):
    return professeur_service.get_all_professeurs(db)


@router.get("/{professeur_id}", response_model=ProfesseurResponse)
def get_professeur(professeur_id: int, db: db_dependancy):
    return professeur_service.get_professeur(db, professeur_id)


@router.put("/{professeur_id}", response_model=ProfesseurResponse)
def update_professeur(professeur_id: int, data: ProfesseurCreate, db: db_dependancy):
    return professeur_service.update_professeur(db, professeur_id, data)


@router.delete("/{professeur_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professeur(professeur_id: int, db: db_dependancy):
    professeur_service.delete_professeur(db, professeur_id)
