from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_presence_examen import PresenceExamenCreate, PresenceExamenResponse
from services import presence_examen_service


router = APIRouter(prefix="/presence-examen", tags=["Presence Examen"])


@router.post("/", response_model=PresenceExamenResponse, status_code=status.HTTP_201_CREATED)
def create_presence_examen(data: PresenceExamenCreate, db: db_dependancy):
    return presence_examen_service.create_presence_examen(db, data)


@router.get("/", response_model=list[PresenceExamenResponse])
def get_presence_examen_list(
    db: db_dependancy,
    skip: int = 0,
    limit: int = 100,
):
    return presence_examen_service.get_all_presence_examens(db, skip, limit)


@router.get("/{presence_id}", response_model=PresenceExamenResponse)
def get_presence_examen(presence_id: int, db: db_dependancy):
    return presence_examen_service.get_presence_examen(db, presence_id)


@router.put("/{presence_id}", response_model=PresenceExamenResponse)
def update_presence_examen(presence_id: int, data: PresenceExamenCreate, db: db_dependancy):
    return presence_examen_service.update_presence_examen(db, presence_id, data)


@router.delete("/{presence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presence_examen(presence_id: int, db: db_dependancy):
    presence_examen_service.delete_presence_examen(db, presence_id)
