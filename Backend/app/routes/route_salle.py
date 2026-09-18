from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_salle import SalleCreate, SalleResponse
from services import salle_service


router = APIRouter(prefix="/salle", tags=["Salles"])


@router.post("/create", response_model=SalleResponse, status_code=status.HTTP_201_CREATED)
def create_salle(data: SalleCreate, db: db_dependancy):
    return salle_service.create_salle(db, data)


@router.get("/all", response_model=list[SalleResponse])
def get_salles(db: db_dependancy):
    return salle_service.get_all_salles(db)


@router.get("/{salle_id}", response_model=SalleResponse)
def get_salle(salle_id: int, db: db_dependancy):
    return salle_service.get_salle(db, salle_id)


@router.put("/{salle_id}", response_model=SalleResponse)
def update_salle(salle_id: int, data: SalleCreate, db: db_dependancy):
    return salle_service.update_salle(db, salle_id, data)


@router.delete("/{salle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salle(salle_id: int, db: db_dependancy):
    salle_service.delete_salle(db, salle_id)
