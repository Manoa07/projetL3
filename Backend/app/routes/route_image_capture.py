from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_image_capture import ImageCaptureCreate, ImageCaptureResponse
from services import image_capture_service


router = APIRouter(prefix="/image-capture", tags=["Image Captures"])


@router.post("/", response_model=ImageCaptureResponse, status_code=status.HTTP_201_CREATED)
def create_image_capture(data: ImageCaptureCreate, db: db_dependancy):
    return image_capture_service.create_image_capture(db, data)


@router.get("/", response_model=list[ImageCaptureResponse])
def get_image_capture_list(
    db: db_dependancy,
    skip: int = 0,
    limit: int = 100,
):
    return image_capture_service.get_all_image_captures(db, skip, limit)


@router.get("/{capture_id}", response_model=ImageCaptureResponse)
def get_image_capture(capture_id: int, db: db_dependancy):
    return image_capture_service.get_image_capture(db, capture_id)


@router.put("/{capture_id}", response_model=ImageCaptureResponse)
def update_image_capture(capture_id: int, data: ImageCaptureCreate, db: db_dependancy):
    return image_capture_service.update_image_capture(db, capture_id, data)


@router.delete("/{capture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image_capture(capture_id: int, db: db_dependancy):
    image_capture_service.delete_image_capture(db, capture_id)
