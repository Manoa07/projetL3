from pydantic import BaseModel

class Stocker_camera(BaseModel):
    id_surveillance:int
    fichier_capture:str
    class Config:
        from_attributes=True
