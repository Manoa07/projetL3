from datetime import datetime
from pydantic import BaseModel

class Create_cours(BaseModel):
    Nom_cours:str
    Prof_cours:str
    Salle_cours:str
    class Config:
        from_attributes = True

class Reponse_cours(BaseModel):
    Id_cours:int
    Nom_cours: str 
    Professeur_cours: str
    Salle_cours:str
    class Config:
        from_attributes=True
