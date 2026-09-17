from typing import Optional
from typing import Optional
<<<<<<< Updated upstream

from pydantic import BaseModel

class Create_surveillance(BaseModel):
    id_examen: Optional[int] = None
    id_eleve: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None
=======
from pydantic import BaseModel

class Create_surveillance(BaseModel):
    id_examen: Optional[int] = None
    id_eleve: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None
    class Config:
        from_attributes=True

class Create_object_alert(BaseModel):
    id_examen:int
    id_eleve:Optional[int] = None
    object_name:str
    confidence:Optional[float] = None

    id_eleve:Optional[int] = None
    Remarque:str
    Status_examen:str
>>>>>>> Stashed changes
    class Config:
        from_attributes=True

class Create_object_alert(BaseModel):
    id_examen:int
    id_eleve:Optional[int] = None
    object_name:str
    confidence:Optional[float] = None

    class Config:
        from_attributes=True

class Eleve_surveillee(BaseModel):
    id_eleve: Optional[int] = None
    id_examen: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None
<<<<<<< Updated upstream
    id_eleve: Optional[int] = None
    id_examen: Optional[int] = None
    Remarque: Optional[str] = None
    Status_examen: Optional[str] = None
=======
    id_eleve:Optional[int] = None
    id_examen:int
    Remarque:str
    Status_examen:str
>>>>>>> Stashed changes
    class Config:
        from_attributes=True
