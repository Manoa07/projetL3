from pydantic import BaseModel


class ProfesseurResponse(BaseModel):
    id_professeur: int
    nom_professeur: str
    prenom_professeur: str
    matricule_professeur: int

    class Config:
        from_attributes = True


class SalleResponse(BaseModel):
    id_salle: int
    nom_salle: str

    class Config:
        from_attributes = True


class MatiereResponse(BaseModel):
    id_matiere: int
    nom_matiere: str

    class Config:
        from_attributes = True
