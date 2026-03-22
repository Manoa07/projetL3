from typing import List
import cv2
from fastapi import APIRouter, File, Form, UploadFile
import numpy as np
from DB.database import db_dependancy
from schema.sch_presence import Create_presence,Presence_eleve
from services.presence_service import create_presence,get_presence_all,get_presence
from modules.presence import SystemePresence
from fastapi import BackgroundTasks

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

@router.post("/detecter")
async def detect(background_tasks: BackgroundTasks,db: db_dependancy,id_cours:int=Form(...) ,file: UploadFile = File(...)):
    systeme=SystemePresence(id_cours,db,seuil_distance=0.8)
    contents = await file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

    resultats = systeme.traiter_image(frame)

    for r in resultats:
        background_tasks.add_task(create_presence_route, r)

    return {"resultats": resultats}