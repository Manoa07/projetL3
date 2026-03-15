import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4

class Create_presence(BaseModel):
    id_presence:Optional[UUID]=uuid4
    id_eleve:Optional[UUID]=uuid4
    id_cours:Optional[UUID]=uuid4
    Status: str
    Heure_presence: datetime 