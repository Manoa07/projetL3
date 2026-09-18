import datetime
from typing import Optional

from pydantic import BaseModel


class Create_presence(BaseModel):
    id_eleve: Optional[int] = None
    id_cours: Optional[int] = None
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class Config:
        from_attributes = True

class Reponse_presence(BaseModel):
    id_eleve: Optional[int] = None
    id_cours: Optional[int] = None
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class Config:
        from_attributes=True

class Presence_eleve(BaseModel):
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class Config:
        from_attributes=True
