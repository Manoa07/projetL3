from pydantic import BaseModel, Field


class MatiereBase(BaseModel):
    nom_matiere: str = Field(min_length=1)


class MatiereCreate(MatiereBase):
    pass


class MatiereResponse(MatiereBase):
    id_matiere: int

    class Config:
        from_attributes = True
