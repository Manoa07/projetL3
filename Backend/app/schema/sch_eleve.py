from typing import List, Optional

from fastapi import File, UploadFile
from pydantic import BaseModel
from fastapi import Form
import json

class Create_eleve(BaseModel):
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int
    embedding:Optional [List[float]]
    @classmethod
    def as_form(
        cls,
        Nom_eleve: str = Form(...),
        Prenom_eleve : str = Form(...),
        Classe_eleve :str = Form(...),
        Numero_eleve : int = Form(...),
        embedding : Optional[List[float]]=Form(...)
    ):
        
        return cls(
            Nom_eleve=Nom_eleve,
            Prenom_eleve=Prenom_eleve,
            Classe_eleve=Classe_eleve,
            Numero_eleve=Numero_eleve,
            embedding=embedding
        )

class eleve_Classe_Nom(BaseModel):
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int

class Reponse_eleve(BaseModel):
    Numero_eleve:int
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    embedding:List[float]
    
    class Config:
        from_attributes=True


class Id_eleve(BaseModel):
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int
    class Config:
        from_attributes=True
