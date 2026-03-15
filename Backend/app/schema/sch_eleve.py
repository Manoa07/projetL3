import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4


class Create_eleve(BaseModel):
    id: Optional[UUID]=uuid4
    Nom: str 
    Prenom:str
    Classe:str
    Numero:int