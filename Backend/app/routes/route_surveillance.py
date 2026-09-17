from typing import List
from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_surveillance import Create_object_alert, Create_surveillance, Eleve_surveillee
from services.surveillance_service import create_object_alert, create_surveillance, voir_eleve
router= APIRouter(prefix="/surveillance",tags=["Surveillance"])

@router.post("/create")
def create_surveillance_route(surveillance:Create_surveillance,db : db_dependancy):
    return create_surveillance(surveillance,db)

@router.post("/object-alert")
def create_object_alert_route(alert:Create_object_alert, db: db_dependancy):
    return create_object_alert(alert, db)

@router.get("/eleve/{id_eleve}", response_model=List[Eleve_surveillee])
def voir_eleve_route(id_eleve:int ,db : db_dependancy):
    return voir_eleve(id_eleve,db)
