from typing import List
from fastapi import APIRouter
from DB.database import db_dependancy
from schema.sch_camera import Stocker_camera
from models.camera import Camera
router= APIRouter(prefix="/camera",tags=["Camera"])

@router.post("/stocker")
def stocker_file (camera: Stocker_camera ,db : db_dependancy):
    new_camera= Camera(
        Id_surveillance=camera.id_surveillance,
        Fichier_capture=camera.fichier_capture
    )
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)
    return new_camera