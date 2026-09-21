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
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    return stats_service.get_stats_presence(db, date_cours, course_id)


@router.get('/presence/presents')
def get_present_students(
    date_cours: date | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Return the list of students marked present for a given date or course."""
    students = stats_service.get_present_students(db, date_cours, course_id)
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


@router.get('/presence/retards')
def get_retard_students(
    date_cours: date | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    students = stats_service.get_retard_students(db, date_cours, course_id)
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


@router.get('/presence/timeseries')
def get_presence_timeseries(days: int = 7, db: Session = Depends(get_db)):
    """Return timeseries for presents and retards for the last `days` days."""
    return stats_service.get_presence_timeseries(db, days=days)
