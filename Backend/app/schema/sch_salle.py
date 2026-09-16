from pydantic import BaseModel, Field


class SalleBase(BaseModel):
    nom_salle: str = Field(min_length=1)


class SalleCreate(SalleBase):
    pass


class SalleResponse(SalleBase):
    id_salle: int

    class Config:
        from_attributes = True
