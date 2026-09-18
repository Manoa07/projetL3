from pydantic import BaseModel, Field


class DetectionBase(BaseModel):
    type_detection: str = Field(min_length=1)
    id_capture_capture: int
    id_eleve_eleve: int


class DetectionCreate(DetectionBase):
    pass


class DetectionResponse(DetectionBase):
    id_detection: int

    class Config:
        from_attributes = True
