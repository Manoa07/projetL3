from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.examen import Examen
from models.matiere import Matiere
from models.presence_examen import PresenceExamen
from models.salle import Salle
from models.surveillance import Surveillance
from models.surveillance_examen import SurveillanceExamen


logger = logging.getLogger(__name__)

def create_examen(examen, db):
    examen_verifie = db.query(Examen).filter(
        and_(
            Examen.date_examen==examen.date_examen,
            Examen.id_cours==examen.id_cours,
            Examen.Salle_examen==examen.salle_examen
        )
    ).first()
    if not examen_verifie:
        new_examen =Examen(
        id_cours=examen.id_cours,
        date_examen=examen.date_examen,
        Heure_debut=examen.heure_debut,
        Heure_fin=examen.heure_fin,
        Salle_examen=examen.salle_examen
        )
        try:
            db.add(new_examen)
            db.commit()
            db.refresh(new_examen)
            return new_examen
        except IntegrityError as e:
            print(e)
    else :
        raise HTTPException(
            status_code=409,
            detail="examen existant"
        )


def get_examen(db):
    examen_verifie = db.query(Examen).all()
    return examen_verifie  # retourne [] si vide


def get_examen_by_id(db, examen_id):
    examen = db.query(Examen).filter(Examen.id_examen == examen_id).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen introuvable")
    return examen


def update_examen(db, examen_id, data):
    examen = get_examen_by_id(db, examen_id)

    if data.id_salle_salle is not None:
        salle = db.query(Salle).filter(
            Salle.id_salle == data.id_salle_salle
        ).first()
        if not salle:
            raise HTTPException(status_code=404, detail="Salle introuvable")

    if data.id_matiere_matiere is not None:
        matiere = db.query(Matiere).filter(
            Matiere.id_matiere == data.id_matiere_matiere
        ).first()
        if not matiere:
            raise HTTPException(status_code=404, detail="Matière introuvable")

    duplicate = db.query(Examen).filter(
        and_(
            Examen.date_examen == data.date_examen,
            Examen.id_salle_salle == data.id_salle_salle,
            Examen.id_matiere_matiere == data.id_matiere_matiere,
            Examen.id_examen != examen_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Examen déjà existant")

    for field, value in {
        "id_cours": data.id_cours,
        "date_examen": data.date_examen,
        "Heure_debut": data.heure_debut,
        "Heure_fin": data.heure_fin,
        "semestre_examen": data.semestre_examen,
        "id_salle_salle": data.id_salle_salle,
        "id_matiere_matiere": data.id_matiere_matiere,
    }.items():
        setattr(examen, field, value)

    try:
        db.commit()
        db.refresh(examen)
        return examen
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour de l'examen", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="L'examen n'a pas pu être mis à jour.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour de l'examen", exc_info=error)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la mise à jour de l'examen.",
        ) from error


def delete_examen(db, examen_id):
    examen = get_examen_by_id(db, examen_id)
    has_presence = db.query(PresenceExamen.id_presence_examen).filter(
        PresenceExamen.id_examen_examen == examen_id
    ).first()
    has_surveillance_examen = db.query(
        SurveillanceExamen.id_surveillance
    ).filter(
        SurveillanceExamen.id_examen_examen == examen_id
    ).first()
    has_surveillance = db.query(Surveillance.Id_surveillance).filter(
        Surveillance.id_examen == examen_id
    ).first()
    if has_presence or has_surveillance_examen or has_surveillance:
        raise HTTPException(
            status_code=409,
            detail="Cet examen possède des surveillances ou présences associées.",
        )

    try:
        db.delete(examen)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        logger.error("Examen référencé lors de la suppression", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="Cet examen possède des surveillances ou présences associées.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression de l'examen", exc_info=error)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la suppression de l'examen.",
        ) from error
    
