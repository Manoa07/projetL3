import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4

class Create_presence(BaseModel):
    id_eleve:int
    id_cours:int
    Status: str
    Heure_presence: datetime 