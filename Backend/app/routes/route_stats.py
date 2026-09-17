from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from DB.database import get_db
from schema.sch_stats import StatsPresence
from services import stats_service


router = APIRouter(
    prefix="/stats",
    tags=["Statistiques"],
)


@router.get("/presence", response_model=StatsPresence)
def get_stats_presence(
    date_cours: date | None = None,
    db: Session = Depends(get_db),
):
    return stats_service.get_stats_presence(db, date_cours)
