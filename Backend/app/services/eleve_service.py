import json
import pickle
import shutil
from sqlite3 import IntegrityError
from uuid import uuid4
from pathlib import Path
import cv2
from fastapi import HTTPException
import numpy as np
from models.eleve import Eleve
from sqlalchemy import and_
from mtcnn import MTCNN
from keras_facenet import FaceNet
detector=MTCNN()
embedder=FaceNet()
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "upload" / "eleve_upload"

def create_eleve(eleve,photo,images,db):
    print("FILES REÇUS :", images)
    eleve_verifie=db.query(Eleve).filter(
        and_(
            Eleve.Nom_eleve==eleve.Nom_eleve,
            Eleve.Prenom_eleve== eleve.Prenom_eleve
        )
    ).first()
    #transformer les images en embedding:
    embedding=[]
    for image in images:
        image.file.seek(0)
        contenue= image.file.read()
        tableau=np.frombuffer(contenue,np.uint8)
        img=cv2.imdecode(tableau,cv2.IMREAD_COLOR)
        if img is None:
            continue
        face=detect_face(img)
        if face is None:
            continue
        if not isinstance(face,np.ndarray):
            continue
        if face.size==0:
            continue
        if face.shape[0]<20 or face.shape[1]<20:
            continue
        emb=embedder.embeddings([face])[0]
        embedding.append(emb)
    if len(embedding)==0:
        raise Exception("Aucun visage trouvé dans l'image ")
    finale_embedding = np.mean(embedding, axis=0)
    
    Filename=f"{uuid4()}_{photo.filename}"
    file_path=UPLOAD_DIR / Filename
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with open(file_path,"wb") as upload:
        shutil.copyfileobj(photo.file, upload)

        
    if not eleve_verifie:
        new_eleve = Eleve(
            Nom_eleve = eleve.Nom_eleve,
            Prenom_eleve= eleve.Prenom_eleve,
            Classe_eleve= eleve.Classe_eleve,
            Numero_eleve= eleve.Numero_eleve,
            photo_eleve=str(file_path),
            embedding=pickle.dumps(finale_embedding)
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
def detect_face(img):
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    if len(img.shape) != 3 or img.shape[2] != 3:
        return None
    resultat=detector.detect_faces(img)
    if not resultat:
        return None
    x, y, w, h = resultat[0]['box']
    x, y = max(0, x), max(0, y)
    face = img[y:y+h, x:x+w]
    if face.size == 0:
        return None
    face = cv2.resize(face, (160, 160))
    print("TYPE FACE:", type(face))
    print("IMG:", type(img), img.shape if img is not None else None)
    print("FACE:", type(face), face.shape if isinstance(face, np.ndarray) else None)
    return face  
def get_eleve(db):
    eleve_verifie=db.query(Eleve).all()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="Aucun eleve trouvé"
        )
    resultat=[]
    for e in eleve_verifie:
        emb=None
        if e.embedding:
                try:
                    if isinstance(e.embedding,bytes):
                        emb= pickle.loads(e.embedding)
                    elif isinstance(e.embedding,str):
                        emb = np.array(json.loads(e.embedding),dtype=np.float32)
                except Exception as err:
                    print("Erreur decodage embedding : ",err)
                    emb=None
        resultat.append({
            "Id_eleve": e.Id_eleve,
            "Numero_eleve": e.Numero_eleve,
            "Nom_eleve": e.Nom_eleve,
            "Prenom_eleve": e.Prenom_eleve,
            "Classe_eleve": e.Classe_eleve,
            "embedding": emb.tolist() if emb is not None else None,
            "presence":[{
                "Date_presence": p.Date_presence.isoformat(),
                "Heure_presence": p.Heure_presence.isoformat(),
                "Status_presence": p.Status_presence,
                "id_cours": p.id_cours,
                "id_eleve": p.id_eleve
            } for p in e.presence]
        })   
    return resultat




def get_eleve_id(eleve_num,eleve_class, db):
    eleve_verifie= db.query(Eleve).filter(
        and_(
            Eleve.Numero_eleve == eleve_num,
            Eleve.Classe_eleve == eleve_class
            )
        ).first()
    if not eleve_verifie:
        raise HTTPException(
            status_code=404,
            detail="Eleve introuvable"
        )
    return eleve_verifie
