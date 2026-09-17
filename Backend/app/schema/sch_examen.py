from typing import Optional

from datetime import date, datetime, time

from pydantic import BaseModel, field_validator


class Create_examen(BaseModel):
    id_cours: Optional[int] = None
    date_examen: Optional[date | datetime] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    semestre_examen: Optional[str] = None
    id_salle_salle: Optional[int] = None
    id_matiere_matiere: Optional[int] = None

    @field_validator("date_examen", mode="after")
    @classmethod
    def normalize_date_examen(cls, value: date | datetime | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.combine(value, time.min)

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
