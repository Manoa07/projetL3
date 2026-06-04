from pydantic import BaseModel
from datetime import date, time

class Create_examen(BaseModel):
    date_examen:date
    heure_debut:time
    heure_fin:time
    salle_examen:str
    id_cours:int
    class Config:
        from_attributes=True

class Voir_examens(BaseModel):
    id_cours:int
    date_examen:date
    Heure_debut:time
    Heure_fin:time
    Salle_examen:str
    class Config:
        from_attributes=True
