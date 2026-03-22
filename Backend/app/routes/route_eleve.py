from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile

from DB.database import db_dependancy
from schema.sch_eleve import Create_eleve , Reponse_eleve ,Id_eleve
from services.eleve_service import create_eleve,get_eleve,get_eleve_id
router= APIRouter(prefix="/eleve",tags=["Eleves"])

@router.post("/create")
def create_eleve_route(
    db: db_dependancy,
    eleve : Create_eleve =Depends(Create_eleve.as_form),
    photo :UploadFile =File(...),
    images : List[UploadFile] = File(...)
    
    ):
    return create_eleve(eleve,photo,images,db)


@router.get("/all",response_model=List[Reponse_eleve])
def get_eleves_route(db:db_dependancy):
    return get_eleve(db)


@router.get("/numero/{eleve_numero}/class/{eleve_class}",response_model=Id_eleve)
def get_eleve_id_route(eleve_numero: int,eleve_class:str, db:db_dependancy):
    return get_eleve_id(eleve_numero,eleve_class,db)
