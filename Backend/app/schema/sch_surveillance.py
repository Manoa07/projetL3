from typing import Optional

from pydantic import BaseModel


class Create_surveillance(BaseModel):
    id_examen: Optional[int] = None
    id_eleve: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None

    class Config:
        from_attributes = True


class Create_object_alert(BaseModel):
    id_examen: int
    id_eleve: Optional[int] = None
    object_name: str
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class Eleve_surveillee(BaseModel):
    id_eleve: Optional[int] = None
    id_examen: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None

    class Config:
        from_attributes = True
