from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_matiere import MatiereCreate, MatiereResponse
from services import matiere_service


router = APIRouter(prefix="/matiere", tags=["Matieres"])


@router.post("/create", response_model=MatiereResponse, status_code=status.HTTP_201_CREATED)
def create_matiere(data: MatiereCreate, db: db_dependancy):
    return matiere_service.create_matiere(db, data)


@router.get("/all", response_model=list[MatiereResponse])
def get_matieres(db: db_dependancy):
    return matiere_service.get_all_matieres(db)


@router.get("/{matiere_id}", response_model=MatiereResponse)
def get_matiere(matiere_id: int, db: db_dependancy):
    return matiere_service.get_matiere(db, matiere_id)


@router.put("/{matiere_id}", response_model=MatiereResponse)
def update_matiere(matiere_id: int, data: MatiereCreate, db: db_dependancy):
    return matiere_service.update_matiere(db, matiere_id, data)


@router.delete("/{matiere_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_matiere(matiere_id: int, db: db_dependancy):
    matiere_service.delete_matiere(db, matiere_id)
