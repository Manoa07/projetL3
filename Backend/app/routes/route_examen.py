from typing import List

from fastapi import APIRouter, status
from DB.database import db_dependancy
from schema.sch_examen import Create_examen, Voir_examens
from services import examen_service
from services.examen_service import create_examen,get_examen
router= APIRouter(prefix="/examen",tags=["Examen"])

@router.post("/create")
def create_examen_route(examen : Create_examen , db : db_dependancy):
    return create_examen(examen , db)

@router.get("/all", response_model=List[Voir_examens])
def get_examen_route(db:db_dependancy):
    return get_examen(db)


@router.put("/{examen_id}", response_model=Voir_examens)
def update_examen_route(
    examen_id: int,
    data: Create_examen,
    db: db_dependancy,
):
    return examen_service.update_examen(db, examen_id, data)


@router.delete("/{examen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_examen_route(examen_id: int, db: db_dependancy):
    examen_service.delete_examen(db, examen_id)
    return None
