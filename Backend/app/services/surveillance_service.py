from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import and_
from models.surveillance import Surveillance

def create_surveillance(surveillance,db):
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
            print(e)
    else:
        # Correction : 401 (Unauthorized) était sémantiquement incorrect.
        # 409 (Conflict) est le bon code quand la ressource existe déjà,
        # cohérent avec presence_service.py et eleve_service.py.
        raise HTTPException(
            status_code=409,
            detail="Surveillance deja existant"
        )
def voir_eleve(id_eleve,db):
    eleve_verifie=db.query(Surveillance).filter(Surveillance.id_eleve==id_eleve).all()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="non trouvé"
        )
    return eleve_verifie
