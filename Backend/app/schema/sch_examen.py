from pydantic import BaseModel
from datetime import datetime ,time 

class Create_examen(BaseModel):
    date_examen:datetime
    heure_debut:time
    heure_fin:time
    salle_examen:str
    id_cours:int
    class Config:
        from_attribute=True

class Voir_examens(BaseModel):
    id_cours:int
    date_examen:datetime
    Heure_debut:time
    Heure_fin:time
    Salle_examen:str
    class Config:
        from_attribute=True