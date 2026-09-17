from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.cours import Cours
from models.matiere import Matiere
from models.professeur import Professeur
from models.salle import Salle
from models.presence import Presence
from models.presence_cours import PresenceCours


logger = logging.getLogger(__name__)


def create_cours(cours,db):
    cours_verifie=db.query(Cours).filter(
        and_(Cours.Nom_cours==cours.Nom_cours,
             Cours.Professeur_cours==cours.Prof_cours
             )
        ).first()
    if not cours_verifie:
        new_cours = Cours(
            Nom_cours = cours.Nom_cours,
            Professeur_cours= cours.Prof_cours,
            Salle_cours=cours.Salle_cours
           )
        try:
            db.add(new_cours)
            db.commit()
            db.refresh(new_cours)
        except IntegrityError as e:
            print(e)
        return new_cours
    else :
        raise HTTPException(
            status_code=201,
            detail="cours creer"
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
