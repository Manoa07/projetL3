from pydantic import BaseModel, Field


class SurveillanceExamenBase(BaseModel):
    remarque_surveillance: str | None = None
    status_examen: str = Field(min_length=1)
    id_capture_capture: int | None = None
    id_examen_examen: int
    id_detection_detection: int | None = None


class SurveillanceExamenCreate(SurveillanceExamenBase):
    pass


class SurveillanceExamenResponse(SurveillanceExamenBase):
    id_surveillance: int

    class Config:
        from_attributes = True
