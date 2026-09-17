from typing import Optional

from pydantic import BaseModel


class StatsPresence(BaseModel):
    total_eleves: int
    presents: int
    absents: int
    retards: int
    taux_presence: float
    alertes_surveillance: Optional[int] = 0

    class Config:
        from_attributes = True
