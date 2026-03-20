from sqlite3 import IntegrityError

from fastapi import HTTPException
from models.eleve import Eleve


def create_eleve(eleve, db):
    eleve_verifie=db.query(Eleve).filter(Eleve.Nom_eleve==eleve.Nom_eleve and Eleve.Prenom_eleve==eleve.Prenom_eleve).first()
    if not eleve_verifie:
        new_eleve = Eleve(
            Nom_eleve = eleve.Nom_eleve,
            Prenom_eleve= eleve.Prenom_eleve,
            Classe_eleve= eleve.Classe_eleve,
            Numero_eleve= eleve.Numero_eleve
            )
        try:
            db.add(new_eleve)
            db.commit()
            db.refresh(new_eleve)
        except IntegrityError as e:
            print(e)
        return new_eleve
    else:
        raise HTTPException(
            status_code=409,
            details="eleve deja existant"
        )

def get_eleve(db):
    eleve_verifie=db.query(Eleve).all()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            details="Aucun eleve trouvé"
        )
    return eleve_verifie

def get_eleve_id(eleve_num, db):
    eleve_verifie= db.query(Eleve).filter(Eleve.Numero_eleve == eleve_num).first()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="Eleve instrouvable"
        )
    return eleve_verifie