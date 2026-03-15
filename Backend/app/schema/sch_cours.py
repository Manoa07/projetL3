import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4

class Create_cours(BaseModel):
    id:Optional[UUID]=uuid4
    Nom_cours:str
    Prof_cours:str
    Date_cours:datetime 