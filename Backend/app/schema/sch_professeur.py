from pydantic import BaseModel, Field


class ProfesseurBase(BaseModel):
    nom_professeur: str = Field(min_length=1)
    prenom_professeur: str = Field(min_length=1)
    matricule_professeur: int


class ProfesseurCreate(ProfesseurBase):
    pass


class ProfesseurResponse(ProfesseurBase):
    id_professeur: int

    class Config:
        from_attributes = True
