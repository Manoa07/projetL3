from datetime import date, time
from pydantic import BaseModel

class Create_cours(BaseModel):
    nom_cours: str
    date_cours: date
    heure_debut_cours: time
    heure_fin_cours: time
    id_professeur_professeur: int
    id_salle_salle: int
    id_matiere_matiere: int
    class Config:
        from_attributes = True

class Reponse_cours(BaseModel):
    Id_cours:int
    Nom_cours: str | None = None
    Professeur_cours: str | None = None
    Salle_cours: str | None = None
    nom_cours: str | None = None
    date_cours: date | None = None
    heure_debut_cours: time | None = None
    heure_fin_cours: time | None = None
    id_professeur_professeur: int | None = None
    id_salle_salle: int | None = None
    id_matiere_matiere: int | None = None
    class Config:
        from_attributes=True
