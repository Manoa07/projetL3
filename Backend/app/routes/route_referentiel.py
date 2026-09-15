from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from DB.database import db_dependancy
from models.professeur import Professeur
from models.salle import Salle
from models.matiere import Matiere

router = APIRouter(tags=["Référentiels"])


class ProfesseurCreate(BaseModel):
    nom_professeur: str
    prenom_professeur: str
    matricule_professeur: int


class NomCreate(BaseModel):
    nom: str


@router.get("/professeur/all")
def professeurs(db: db_dependancy):
    return db.query(Professeur).order_by(Professeur.nom_professeur).all()


@router.post("/professeur/create")
def create_professeur(data: ProfesseurCreate, db: db_dependancy):
    # Correction : .dict() est déprécié en Pydantic v2 → .model_dump()
    value = Professeur(**data.model_dump())
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


@router.get("/salle/all")
def salles(db: db_dependancy):
    return db.query(Salle).order_by(Salle.nom_salle).all()


@router.post("/salle/create")
def create_salle(data: NomCreate, db: db_dependancy):
    value = Salle(nom_salle=data.nom.strip())
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


@router.get("/matiere/all")
def matieres(db: db_dependancy):
    return db.query(Matiere).order_by(Matiere.nom_matiere).all()


@router.post("/matiere/create")
def create_matiere(data: NomCreate, db: db_dependancy):
    value = Matiere(nom_matiere=data.nom.strip())
    db.add(value)
    db.commit()
    db.refresh(value)
    return value
