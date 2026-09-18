import logging

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models.cours import Cours
from models.matiere import Matiere
from models.professeur import Professeur
from models.salle import Salle
from models.presence import Presence
from models.presence_cours import PresenceCours


logger = logging.getLogger(__name__)


def create_cours(cours, db):
    professeur = db.query(Professeur).filter(
        Professeur.id_professeur == cours.id_professeur_professeur
    ).first()
    if not professeur:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    salle = db.query(Salle).filter(
        Salle.id_salle == cours.id_salle_salle
    ).first()
    if not salle:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    matiere = db.query(Matiere).filter(
        Matiere.id_matiere == cours.id_matiere_matiere
    ).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière introuvable")

    cours_verifie = db.query(Cours).filter(
        and_(
            Cours.Nom_cours == cours.nom_cours,
            Cours.date_cours == cours.date_cours,
            Cours.id_professeur_professeur == cours.id_professeur_professeur,
        )
    ).first()
    if not cours_verifie:
        new_cours = Cours(
            Nom_cours=cours.nom_cours,
            date_cours=cours.date_cours,
            heure_debut_cours=cours.heure_debut_cours,
            heure_fin_cours=cours.heure_fin_cours,
            id_professeur_professeur=cours.id_professeur_professeur,
            id_salle_salle=cours.id_salle_salle,
            id_matiere_matiere=cours.id_matiere_matiere,
        )
        try:
            db.add(new_cours)
            db.commit()
            db.refresh(new_cours)
            return new_cours
        except IntegrityError as e:
            db.rollback()
            logger.error("Erreur d'intégrité lors de la création du cours", exc_info=e)
            raise HTTPException(
                status_code=400,
                detail="Erreur d'intégrité de la base de données."
            )
        except Exception as e:
            db.rollback()
            logger.error("Erreur lors de l'enregistrement du cours", exc_info=e)
            raise HTTPException(
                status_code=500,
                detail="Erreur interne lors de l'enregistrement du cours."
            )
    else:
        raise HTTPException(
            status_code=409,
            detail="Cours déjà existant"
        )
def get_cours(db):
    cours_verifie = db.query(Cours).all()
    return cours_verifie  # retourne [] si vide, pas une erreur 404


def get_cours_by_id(db, cours_id):
    cours = db.query(Cours).filter(Cours.Id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    return cours


def update_cours(db, cours_id, data):
    cours = get_cours_by_id(db, cours_id)

    professeur = db.query(Professeur).filter(
        Professeur.id_professeur == data.id_professeur_professeur
    ).first()
    if not professeur:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    salle = db.query(Salle).filter(
        Salle.id_salle == data.id_salle_salle
    ).first()
    if not salle:
        raise HTTPException(status_code=404, detail="Salle introuvable")

    matiere = db.query(Matiere).filter(
        Matiere.id_matiere == data.id_matiere_matiere
    ).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matière introuvable")

    duplicate = db.query(Cours).filter(
        and_(
            Cours.Nom_cours == data.nom_cours,
            Cours.date_cours == data.date_cours,
            Cours.id_professeur_professeur == data.id_professeur_professeur,
            Cours.Id_cours != cours_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Cours déjà existant")

    for field, value in {
        "Nom_cours": data.nom_cours,
        "date_cours": data.date_cours,
        "heure_debut_cours": data.heure_debut_cours,
        "heure_fin_cours": data.heure_fin_cours,
        "id_professeur_professeur": data.id_professeur_professeur,
        "id_salle_salle": data.id_salle_salle,
        "id_matiere_matiere": data.id_matiere_matiere,
    }.items():
        setattr(cours, field, value)

    try:
        db.commit()
        db.refresh(cours)
        return cours
    except IntegrityError as error:
        db.rollback()
        logger.error("Erreur d'intégrité lors de la mise à jour du cours", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="Le cours n'a pas pu être mis à jour.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la mise à jour du cours", exc_info=error)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la mise à jour du cours.",
        ) from error


def delete_cours(db, cours_id):
    cours = get_cours_by_id(db, cours_id)
    has_presence = db.query(Presence.id_presence).filter(
        Presence.id_cours == cours_id
    ).first()
    has_presence_cours = db.query(PresenceCours.id_presence_cours).filter(
        PresenceCours.id_cours_cours == cours_id
    ).first()
    if has_presence or has_presence_cours:
        raise HTTPException(
            status_code=409,
            detail="Ce cours possède des présences associées.",
        )

    try:
        db.delete(cours)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        logger.error("Cours référencé lors de la suppression", exc_info=error)
        raise HTTPException(
            status_code=409,
            detail="Ce cours possède des présences associées.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.error("Erreur lors de la suppression du cours", exc_info=error)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la suppression du cours.",
        ) from error
