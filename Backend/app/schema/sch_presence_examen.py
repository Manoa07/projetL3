from datetime import time

from pydantic import BaseModel, Field


class PresenceExamenBase(BaseModel):
    status_presence_examen: str = Field(min_length=1)
    heure_arrive_examen: time | None = None
    id_eleve_eleve: int
    id_examen_examen: int


class PresenceExamenCreate(PresenceExamenBase):
    pass


class PresenceExamenResponse(PresenceExamenBase):
    id_presence_examen: int

    class Config:
        from_attributes = True
