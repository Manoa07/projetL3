import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID, uuid4


class Create_eleve(BaseModel):
    Nom: str 
    Prenom:str
    Classe:str
    Numero:int

class Reponse_eleve(BaseModel):
    id:int
    Nom: str 
    Prenom:str
    Classe:str
    Numero:int
    class config:
        from_attributes=True


class Id_eleve(BaseModel):
    id:int