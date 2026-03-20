from fastapi import File, UploadFile
from pydantic import BaseModel
from fastapi import Form

class Create_eleve(BaseModel):
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int
    @classmethod
    def as_form(
        cls,
        Nom_eleve: str = Form(...),
        Prenom_eleve : str = Form(...),
        Classe_eleve :str = Form(...),
        Numero_eleve : int = Form(...)
    ):
        return cls(
            Nom_eleve=Nom_eleve,
            Prenom_eleve=Prenom_eleve,
            Classe_eleve=Classe_eleve,
            Numero_eleve=Numero_eleve
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
    
    class Config:
        from_attributes=True


class Id_eleve(BaseModel):
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int
    class Config:
        from_attributes=True
