from typing import Optional

from pydantic import BaseModel
from datetime import datetime, time

class Create_examen(BaseModel):
    id_cours: Optional[int] = None
    date_examen: Optional[datetime] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    semestre_examen: Optional[str] = None
    id_salle_salle: Optional[int] = None
    id_matiere_matiere: Optional[int] = None
    class Config:
        from_attributes=True

class Voir_examens(BaseModel):
    id_examen: int                      # BUG-11 : exposer l'id pour que le frontend puisse l'utiliser
    id_cours: Optional[int] = None
    date_examen: Optional[datetime] = None
    Heure_debut: Optional[time] = None
    Heure_fin: Optional[time] = None
    semestre_examen: Optional[str] = None
    id_salle_salle: int | None = None
    id_matiere_matiere: int | None = None
    class Config:
        from_attributes = True
