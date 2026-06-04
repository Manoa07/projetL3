from pydantic import BaseModel

class Create_surveillance(BaseModel):
    id_examen:int
    id_eleve:int
    Remarque:str
    Status_examen:str
    class Config:
        from_attributes=True

class Eleve_surveillee(BaseModel):
    id_eleve:int
    id_examen:int
    Remarque:str
    Status_examen:str
    class Config:
        from_attributes=True
