from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_presence_cours import PresenceCoursCreate, PresenceCoursResponse
from services import presence_cours_service


router = APIRouter(prefix="/presence-cours", tags=["Presence Cours"])


@router.post("/", response_model=PresenceCoursResponse, status_code=status.HTTP_201_CREATED)
def create_presence_cours(data: PresenceCoursCreate, db: db_dependancy):
    return presence_cours_service.create_presence_cours(db, data)


@router.get("/", response_model=list[PresenceCoursResponse])
def get_presence_cours_list(
    db: db_dependancy,
    skip: int = 0,
    limit: int = 100,
):
    return presence_cours_service.get_all_presence_cours(db, skip, limit)


@router.get("/{presence_id}", response_model=PresenceCoursResponse)
def get_presence_cours(presence_id: int, db: db_dependancy):
    return presence_cours_service.get_presence_cours(db, presence_id)


@router.put("/{presence_id}", response_model=PresenceCoursResponse)
def update_presence_cours(presence_id: int, data: PresenceCoursCreate, db: db_dependancy):
    return presence_cours_service.update_presence_cours(db, presence_id, data)


@router.delete("/{presence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presence_cours(presence_id: int, db: db_dependancy):
    presence_cours_service.delete_presence_cours(db, presence_id)
