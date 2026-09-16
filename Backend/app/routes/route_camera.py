from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_camera import CameraResponse, Stocker_camera
from services import camera_service

router= APIRouter(prefix="/camera",tags=["Camera"])

@router.post("/stocker", response_model=CameraResponse)
def stocker_file (camera: Stocker_camera ,db : db_dependancy):
    return camera_service.create_camera(db, camera)