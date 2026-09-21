import logging
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models.cours import Cours
from models.eleve import Eleve
from models.presence import Presence


logger = logging.getLogger(__name__)


def determine_presence_status(heure_presence: time, heure_debut_cours: time, delai_retard_minutes: int = 15) -> str:
    """Détermine le statut d'une présence selon l'heure d'arrivée."""
    if heure_presence is None or heure_debut_cours is None:
        return "present"

    debut = datetime.combine(date.today(), heure_debut_cours)
    arrivee = datetime.combine(date.today(), heure_presence)
    seuil_retard = debut + timedelta(minutes=delai_retard_minutes)
    return "retard" if arrivee > seuil_retard else "present"


def is_course_finished(cours: Cours, now: datetime | None = None) -> bool:
    """Vérifie si un cours est déjà terminé."""
    if cours is None or cours.heure_fin_cours is None:
        return False
    reference = now or datetime.now()
    fin = datetime.combine(reference.date(), cours.heure_fin_cours)
    return reference > fin


def get_course_presence_summary(db, cours_id: int, target_date: date | None = None):
    """Retourne le nombre de présents, absents et retardataires pour un cours."""
    cours = db.query(Cours).filter(Cours.Id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    jour = target_date or (cours.date_cours or date.today())
    total_eleves = db.query(Eleve.Id_eleve).count() or 0

    presence_rows = (
        db.query(Presence)
        .filter(Presence.id_cours == cours_id, Presence.Date_presence == jour)
        .all()
    )

    presents = 0
    retards = 0
    for row in presence_rows:
        status = (row.Status_presence or "").strip().lower()
        if status == "present":
            presents += 1
        elif status == "retard":
            retards += 1

    absents = max(total_eleves - presents - retards, 0)
    return {
        "cours_id": cours_id,
        "date_cours": jour.isoformat(),
        "present": presents,
        "retard": retards,
        "absent": absents,
        "total_eleves": total_eleves,
    }


def create_presence(presence, db):
    eleve = db.query(Eleve).filter(Eleve.Id_eleve == presence.id_eleve).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    cours = db.query(Cours).filter(Cours.Id_cours == presence.id_cours).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    if cours.date_cours is not None and presence.Date_presence > cours.date_cours:
        raise HTTPException(
            status_code=400,
            detail="La date de présence ne correspond pas au cours."
        )

    if is_course_finished(cours):
        raise HTTPException(
            status_code=400,
            detail="Le cours est déjà terminé. Le statut de cet élève est considéré comme absent."
        )

    determined_status = determine_presence_status(
        presence.Heure_presence,
        cours.heure_debut_cours,
        delai_retard_minutes=15,
    )

    presence_verifie = db.query(Presence).filter(
        and_(
            Presence.id_eleve == presence.id_eleve,
            Presence.id_cours == presence.id_cours,
            Presence.Date_presence == presence.Date_presence,
        )
    ).first()

    if presence_verifie:
        raise HTTPException(status_code=409, detail="presence existant")

    new_presence = Presence(
        id_cours=presence.id_cours,
        id_eleve=presence.id_eleve,
        Status_presence=determined_status,
        Heure_presence=presence.Heure_presence,
        Date_presence=presence.Date_presence,
    )
    try:
        db.add(new_presence)
        db.commit()
        db.refresh(new_presence)
        return new_presence
    except IntegrityError as e:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la création de la présence", exc_info=e)
        raise HTTPException(
            status_code=409,
            detail="La présence n'a pas pu être enregistrée.",
        ) from e
    except Exception as e:
        db.rollback()
        logger.error("Erreur lors de la création de la présence", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la création de la présence.",
        ) from e


def get_presence_all(eleve_id, db):
    return db.query(Presence).filter(Presence.id_eleve == eleve_id).all()  # [] si vide


def get_presence(eleve_id, db):
    eleve_verifie = db.query(Presence).filter(Presence.id_eleve == eleve_id).first()
    if not eleve_verifie:
        raise HTTPException(status_code=404, detail="eleve non trouvé")
    return eleve_verifie
