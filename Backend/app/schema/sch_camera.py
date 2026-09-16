from typing import Optional

from pydantic import BaseModel

class Stocker_camera(BaseModel):
    id_surveillance: Optional[int] = None
    fichier_capture: Optional[str] = None
    class Config:
        from_attributes=True


class CameraResponse(BaseModel):
    Id_Capture: int
    Id_surveillance: int | None = None
    Fichier_capture: str | None = None

    class Config:
        from_attributes = True
