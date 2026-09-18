from datetime import time

from pydantic import BaseModel, Field


class PresenceCoursBase(BaseModel):
    status_presence_cours: str = Field(min_length=1)
    heure_arrive_cours: time
    heure_depart_cours: time | None = None
    id_cours_cours: int
    id_eleve_eleve: int


class PresenceCoursCreate(PresenceCoursBase):
    pass


class PresenceCoursResponse(PresenceCoursBase):
    id_presence_cours: int

    class Config:
        from_attributes = True
