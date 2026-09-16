import logging

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models.cours import Cours
from models.matiere import Matiere
from models.professeur import Professeur
from models.salle import Salle


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
