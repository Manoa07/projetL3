from pydantic import BaseModel
from datetime import date, time

class Create_examen(BaseModel):
    date_examen:date
    heure_debut:time
    heure_fin:time
    semestre_examen: str
    id_salle_salle: int
    id_matiere_matiere: int
    class Config:
        from_attributes=True

class Voir_examens(BaseModel):
    date_examen:date
    Heure_debut:time
    Heure_fin:time
    semestre_examen: str | None = None
    id_salle_salle: int | None = None
    id_matiere_matiere: int | None = None
    class Config:
        from_attributes=True
