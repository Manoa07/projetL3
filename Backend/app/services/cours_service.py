from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.cours import Cours


def create_cours(cours,db):
    cours_verifie=db.query(Cours).filter(
        and_(Cours.nom_cours == cours.nom_cours,
             Cours.date_cours == cours.date_cours,
             Cours.id_professeur_professeur == cours.id_professeur_professeur)
        ).first()
    if not cours_verifie:
        new_cours = Cours(
            Nom_cours = cours.nom_cours,
            date_cours = cours.date_cours,
            heure_debut_cours = cours.heure_debut_cours,
            heure_fin_cours = cours.heure_fin_cours,
            id_professeur_professeur = cours.id_professeur_professeur,
            id_salle_salle = cours.id_salle_salle,
            id_matiere_matiere = cours.id_matiere_matiere
           )
        try:
            db.add(new_cours)
            db.commit()
            db.refresh(new_cours)
        except IntegrityError as e:
            print(e)
        return new_cours
    else:
        # Cours déjà existant → retourner les infos existantes
        return cours_verifie
def get_cours(db):
    cours_verifie = db.query(Cours).all()
    if not cours_verifie:
        raise HTTPException(
            status_code=404,
            detail="Aucun cours trouvé"
        )

    return cours_verifie
