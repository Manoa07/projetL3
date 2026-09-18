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


@router.get('/presence/presents')
def get_present_students(
    date_cours: date | None = None,
    db: Session = Depends(get_db),
):
    """Return the list of students marked present for a given date."""
    students = stats_service.get_present_students(db, date_cours)
    # Serialize minimal student info
    return [
        {
            'Id_eleve': s.Id_eleve,
            'Nom_eleve': s.Nom_eleve,
            'Prenom_eleve': s.Prenom_eleve,
            'Classe_eleve': s.Classe_eleve,
            'Numero_eleve': s.Numero_eleve,
        }
        for s in students
    ]
