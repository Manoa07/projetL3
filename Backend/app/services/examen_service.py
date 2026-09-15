from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.examen import Examen

def create_examen(examen, db):
    examen_verifie = db.query(Examen).filter(
        and_(
            Examen.date_examen == examen.date_examen,
            Examen.Heure_debut == examen.heure_debut,   # BUG-07 : vérifier aussi l'heure
            Examen.id_salle_salle == examen.id_salle_salle,
            Examen.id_matiere_matiere == examen.id_matiere_matiere
        )
    ).first()
    if not examen_verifie:
        new_examen =Examen(
        date_examen=examen.date_examen,
        Heure_debut=examen.heure_debut,
        Heure_fin=examen.heure_fin,
        semestre_examen=examen.semestre_examen,
        id_salle_salle=examen.id_salle_salle,
        id_matiere_matiere=examen.id_matiere_matiere
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
    
