from typing import List
from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_presence import Create_presence,Presence_eleve
from services.presence_service import create_presence,get_presence_all,get_presence
router= APIRouter(prefix="/presence",tags=["Presence"])

@router.post("/create")
def create_presence_route(presence: Create_presence, db:db_dependancy):
    return create_presence(presence,db)

@router.get("/eleve/{eleve_id}",response_model=List[Presence_eleve])
def get_presence_all_route(eleve_id :int,db:db_dependancy):
    return get_presence_all(eleve_id,db)
@router.get("/eleve_last/{eleve_id}",response_model=Presence_eleve)
def get_presence_route(eleve_id :int,db:db_dependancy):
    return get_presence(eleve_id,db)
