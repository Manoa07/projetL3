import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4
from schema.sch_cours import cours_date
from schema.sch_eleve import eleve_Classe_Nom

class Create_presence(BaseModel):
    id_eleve :int
    id_cours:int
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class Config:
        from_attribute = True

class Reponse_presence(BaseModel):
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class config:
        from_attribute=True

class Presence_eleve(BaseModel):
    Status_presence: str
    Heure_presence: datetime.time
    Date_presence : datetime.date
    class config:
        from_attribute=True