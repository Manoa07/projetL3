from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.cours import Cours


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
    if not cours_verifie:
        raise HTTPException(
            status_code=404,
            detail="Aucun cours trouvé"
        )

    return cours_verifie

