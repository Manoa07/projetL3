from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_detection import DetectionCreate, DetectionResponse
from services import detection_service


router = APIRouter(prefix="/detection", tags=["Detections"])


@router.post("/", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
def create_detection(data: DetectionCreate, db: db_dependancy):
    return detection_service.create_detection(db, data)


@router.get("/", response_model=list[DetectionResponse])
def get_detection_list(
    db: db_dependancy,
    skip: int = 0,
    limit: int = 100,
):
    return detection_service.get_all_detections(db, skip, limit)


@router.get("/{detection_id}", response_model=DetectionResponse)
def get_detection(detection_id: int, db: db_dependancy):
    return detection_service.get_detection(db, detection_id)


@router.put("/{detection_id}", response_model=DetectionResponse)
def update_detection(detection_id: int, data: DetectionCreate, db: db_dependancy):
    return detection_service.update_detection(db, detection_id, data)


@router.delete("/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_detection(detection_id: int, db: db_dependancy):
    detection_service.delete_detection(db, detection_id)
