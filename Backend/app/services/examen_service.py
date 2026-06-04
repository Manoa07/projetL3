from sqlite3 import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.examen import Examen

def create_examen(examen,db):
    examen_verifie=db.query(Examen).filter(
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
def get_examen(id_cours,db):
    examen_verifie=db.query(Examen).filter(Examen.id_cours==id_cours).all()
    if not examen_verifie:
        raise HTTPException(
            status_code=404,
            detail="examen non trouvé"
        )
    return examen_verifie
    
