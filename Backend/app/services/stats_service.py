from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.cours import Cours
from models.eleve import Eleve
from models.presence import Presence
from models.surveillance import Surveillance
from schema.sch_stats import StatsPresence


def _resolve_target_date(db: Session, date_cours: date | None = None, course_id: int | None = None):
    if date_cours is not None:
        return date_cours
    if course_id is not None:
        cours = db.query(Cours).filter(Cours.Id_cours == course_id).first()
        if cours and cours.date_cours:
            return cours.date_cours
    return date.today()


def get_stats_presence(
    db: Session,
    date_cours: date | None = None,
    course_id: int | None = None,
) -> StatsPresence:
    target_date = _resolve_target_date(db, date_cours, course_id)

    total_eleves = db.query(func.count(func.distinct(Eleve.Id_eleve))).scalar() or 0

    presence_query = db.query(Presence).filter(Presence.Date_presence == target_date)
    if course_id is not None:
        presence_query = presence_query.filter(Presence.id_cours == course_id)

    presents = (
        presence_query.filter(func.lower(Presence.Status_presence) == "present")
        .count()
    )

    retards = (
        presence_query.filter(func.lower(Presence.Status_presence) == "retard")
        .count()
    )

    alertes_surveillance = (
        db.query(func.count(Surveillance.Id_surveillance))
        .filter(func.lower(Surveillance.Status_examen) != "normal")
        .scalar()
        or 0
    )

    absents = max(total_eleves - presents - retards, 0)
    taux_presence = round((presents / total_eleves) * 100, 2) if total_eleves else 0.0

    return StatsPresence(
        total_eleves=total_eleves,
        presents=presents,
        absents=absents,
        retards=retards,
        taux_presence=taux_presence,
        alertes_surveillance=alertes_surveillance,
    )


def get_present_students(db: Session, date_cours: date | None = None, course_id: int | None = None):
    """Return a list of Eleve objects who are marked present for target_date."""
    target_date = _resolve_target_date(db, date_cours, course_id)
    presents_q = (
        db.query(Eleve)
        .join(Presence, Presence.id_eleve == Eleve.Id_eleve)
        .filter(Presence.Date_presence == target_date)
    )
    if course_id is not None:
        presents_q = presents_q.filter(Presence.id_cours == course_id)
    presents_q = presents_q.filter(func.lower(Presence.Status_presence) == "present").distinct()
    return presents_q.all()


def get_retard_students(db: Session, date_cours: date | None = None, course_id: int | None = None):
    """Return a list of Eleve objects who are marked 'retard' for target_date."""
    target_date = _resolve_target_date(db, date_cours, course_id)
    q = (
        db.query(Eleve)
        .join(Presence, Presence.id_eleve == Eleve.Id_eleve)
        .filter(Presence.Date_presence == target_date)
    )
    if course_id is not None:
        q = q.filter(Presence.id_cours == course_id)
    q = q.filter(func.lower(Presence.Status_presence) == "retard").distinct()
    return q.all()


def get_presence_timeseries(db: Session, days: int = 7):
    """Return timeseries counts of presents and retards for the last `days` days."""
    from datetime import date, timedelta

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # initialize map of dates
    dates = [start_date + timedelta(days=i) for i in range(days)]
    result = {d: {"presents": 0, "retards": 0} for d in dates}

    rows = (
        db.query(Presence.Date_presence, Presence.Status_presence, func.count(Presence.id_presence))
        .filter(Presence.Date_presence >= start_date, Presence.Date_presence <= end_date)
        .group_by(Presence.Date_presence, func.lower(Presence.Status_presence))
        .all()
    )

    for row in rows:
        d, status, count = row
        key = d
        if key in result:
            if status and status.lower() == "retard":
                result[key]["retards"] = int(count)
            elif status and status.lower() == "present":
                result[key]["presents"] = int(count)

    # serialize
    serialized = []
    for d in dates:
        serialized.append({"date": d.isoformat(), "presents": result[d]["presents"], "retards": result[d]["retards"]})
    return serialized
