import pickle
import shutil
from sqlite3 import IntegrityError
from uuid import uuid4
from fastapi import HTTPException
from models.eleve import Eleve
import os
from sqlalchemy import and_
UPLOAD_DIR="upload/eleve_upload"

def create_eleve(eleve,photo,embedding,db):
    eleve_verifie=db.query(Eleve).filter(
        and_(
            Eleve.Nom_eleve==eleve.Nom_eleve,
            Eleve.Prenom_eleve== eleve.Prenom_eleve
        )
    ).first()
    Filename=f"{uuid4()}_{photo.filename}"

    file_path=os.path.join(UPLOAD_DIR,Filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path,"wb") as upload:
        shutil.copyfileobj(photo.file, upload)

    embedding_blob=None

    if embedding is not None:
        embedding_blob=pickle.dumps(embedding)
        
    if not eleve_verifie:
        new_eleve = Eleve(
            Nom_eleve = eleve.Nom_eleve,
            Prenom_eleve= eleve.Prenom_eleve,
            Classe_eleve= eleve.Classe_eleve,
            Numero_eleve= eleve.Numero_eleve,
            photo_eleve=file_path,
            embedding=embedding_blob
            )
        try:
            db.add(new_eleve)
            db.commit()
            db.refresh(new_eleve)
        except IntegrityError as e:
            print(e)
        return {
            "Numero_eleve": new_eleve.Numero_eleve,
            "Nom_eleve": new_eleve.Nom_eleve,
            "Prenom_eleve": new_eleve.Prenom_eleve,
            "Classe_eleve": new_eleve.Classe_eleve
        }
    else:
        raise HTTPException(
            status_code=409,
            detail="eleve deja existant"
        )

def get_eleve(db):
    eleve_verifie=db.query(Eleve).all()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="Aucun eleve trouvé"
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