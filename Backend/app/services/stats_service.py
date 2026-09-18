from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.eleve import Eleve
from models.presence import Presence
from models.surveillance import Surveillance
from schema.sch_stats import StatsPresence


def get_stats_presence(
    db: Session,
    date_cours: date | None = None,
) -> StatsPresence:
    target_date = date_cours or date.today()

    total_eleves = db.query(func.count(func.distinct(Eleve.Id_eleve))).scalar() or 0

    presents = (
        db.query(func.count(func.distinct(Presence.id_eleve)))
        .filter(
            Presence.Date_presence == target_date,
            func.lower(Presence.Status_presence) == "present",
        )
        .scalar()
        or 0
    )

    retards = (
        db.query(func.count(func.distinct(Presence.id_eleve)))
        .filter(
            Presence.Date_presence == target_date,
            func.lower(Presence.Status_presence) == "retard",
        )
        .scalar()
        or 0
    )

    alertes_surveillance = (
        db.query(func.count(Surveillance.Id_surveillance))
        .filter(func.lower(Surveillance.Status_examen) != "normal")
        .scalar()
        or 0
    )

    absents = max(total_eleves - presents, 0)
    taux_presence = round((presents / total_eleves) * 100, 2) if total_eleves else 0.0

    return StatsPresence(
        total_eleves=total_eleves,
        presents=presents,
        absents=absents,
        retards=retards,
        taux_presence=taux_presence,
        alertes_surveillance=alertes_surveillance,
    )


def get_present_students(db: Session, date_cours: date | None = None):
    """Return a list of Eleve objects who are marked present for target_date."""
    target_date = date_cours or date.today()
    # Join Presence -> Eleve and filter by date and status
    presents_q = (
        db.query(Eleve)
        .join(Presence, Presence.id_eleve == Eleve.Id_eleve)
        .filter(
            Presence.Date_presence == target_date,
            func.lower(Presence.Status_presence) == "present",
        )
        .distinct()
    )
    return presents_q.all()
