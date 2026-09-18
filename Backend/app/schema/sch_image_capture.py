from datetime import date, time

from pydantic import BaseModel, Field


class ImageCaptureBase(BaseModel):
    fichier_capture: str = Field(min_length=1)
    date_capture: date
    heure_capture: time


class ImageCaptureCreate(ImageCaptureBase):
    pass


class ImageCaptureResponse(ImageCaptureBase):
    id_capture: int

    class Config:
        from_attributes = True
