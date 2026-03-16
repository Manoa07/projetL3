from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Create_cours(BaseModel):
    Nom_cours:str
    Prof_cours:str
    Date_cours:datetime 
    Salle_cours:str
    class Config:
        from_attribute = True
class cours_date(BaseModel):
    Nom_cours:str
    Date_cours:datetime

class Reponse_cours(BaseModel):
    Nom_cours: str 
    Professeur_cours: str
    Date_cours :datetime
    Salle_cours:str
    class config:
        from_attributes=True