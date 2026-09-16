from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.cours import Cours


def create_cours(cours, db):
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
            raise HTTPException(
                status_code=400,
                detail=f"Erreur d'intégrité de la base de données : {e.orig}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'enregistrement : {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=409,
            detail="Cours déjà existant"
        )
def get_cours(db):
    cours_verifie = db.query(Cours).all()
    return cours_verifie  # retourne [] si vide, pas une erreur 404
