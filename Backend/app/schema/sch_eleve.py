from pydantic import BaseModel

class Create_eleve(BaseModel):
    Nom_eleve: str 
    Prenom_eleve:str
    Classe_eleve:str
    Numero_eleve:int
    class Config:
        from_attribute = True
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
