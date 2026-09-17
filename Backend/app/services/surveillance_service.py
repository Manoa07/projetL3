import logging

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models.eleve import Eleve
from models.examen import Examen
from models.surveillance import Surveillance
from schema.sch_surveillance import Create_surveillance


logger = logging.getLogger(__name__)

def create_surveillance(surveillance,db):
    eleve = db.query(Eleve).filter(Eleve.Id_eleve == surveillance.id_eleve).first()
    if not eleve:
        raise HTTPException(status_code=404, detail="Élève introuvable")

    examen = db.query(Examen).filter(Examen.id_examen == surveillance.id_examen).first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen introuvable")

    surveillance_verifie=db.query(Surveillance).filter(
        and_(
            Surveillance.id_eleve==surveillance.id_eleve,
            Surveillance.id_examen==surveillance.id_examen
        )
    ).first()
    if not surveillance_verifie:
        new_surveillance=Surveillance(
            id_examen=surveillance.id_examen,
            id_eleve=surveillance.id_eleve,
            Status_examen=surveillance.Status_examen,
            Remarque=surveillance.Remarque
            )
        try:
            db.add(new_surveillance)
            db.commit()
            db.refresh(new_surveillance)
            return new_surveillance
        except IntegrityError as e:
            db.rollback()
            logger.error("Erreur d'intégrité lors de la création de la surveillance", exc_info=e)
            raise HTTPException(
                status_code=409,
                detail="La surveillance n'a pas pu être enregistrée.",
            ) from e
        except Exception as e:
            db.rollback()
            logger.error("Erreur lors de la création de la surveillance", exc_info=e)
            raise HTTPException(
                status_code=500,
                detail="Erreur interne lors de la création de la surveillance.",
            ) from e
    else:
        # Correction : 401 (Unauthorized) était sémantiquement incorrect.
        # 409 (Conflict) est le bon code quand la ressource existe déjà,
        # cohérent avec presence_service.py et eleve_service.py.
        raise HTTPException(
            status_code=409,   # BUG-09 : 409 Conflict, pas 401 Unauthorized
            detail="Surveillance déjà existante"
        )
def voir_eleve(id_eleve, db):
    eleve_verifie = db.query(Surveillance).filter(Surveillance.id_eleve == id_eleve).all()
    return eleve_verifie  # retourne [] si vide

def create_object_alert(alert, db):
    if not db.query(Examen).filter(Examen.id_examen == alert.id_examen).first():
        raise HTTPException(status_code=404, detail="Examen non trouve")

    confidence = (
        f" ({alert.confidence:.0%})"
        if alert.confidence is not None
        else ""
    )
    surveillance = Create_surveillance(
        id_examen=alert.id_examen,
        id_eleve=alert.id_eleve,
        Status_examen="suspect",
        Remarque=f"Objet interdit detecte: {alert.object_name}{confidence}",
    )
    return create_surveillance(surveillance, db)
