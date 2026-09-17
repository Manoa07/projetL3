from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from DB.database import db_dependancy
from schema.sch_eleve import Create_eleve , Reponse_eleve ,Id_eleve
from services.eleve_service import (
    create_eleve,
    delete_eleve,
    get_eleve,
    get_eleve_embeddings,
    get_eleve_id,
    update_eleve,
)
router= APIRouter(prefix="/eleve",tags=["Eleves"])

@router.post("/create")
def create_eleve_route(
    db: db_dependancy,
    eleve : Create_eleve =Depends(Create_eleve.as_form),
    photo : UploadFile =File(...),
    images : Optional[List[UploadFile]] = File(None)
    
    ):
    return create_eleve(eleve,photo,images,db)


@router.get("/all",response_model=List[Reponse_eleve])
def get_eleves_route(db:db_dependancy):
    return get_eleve(db)


# Endpoint interne pour le chargement de la base de reconnaissance faciale
@router.get("/embeddings", response_model=dict[int, List[float]])
def get_eleve_embeddings_route(db: db_dependancy):
    return get_eleve_embeddings(db)


@router.get("/numero/{eleve_numero}/class/{eleve_class}",response_model=Id_eleve)
def get_eleve_id_route(eleve_numero: int,eleve_class:str, db:db_dependancy):
    return get_eleve_id(eleve_numero,eleve_class,db)


@router.put("/{eleve_id}", response_model=Reponse_eleve)
def update_eleve_route(
    eleve_id: int,
    data: Create_eleve,
    db: db_dependancy,
):
    return update_eleve(db, eleve_id, data)


@router.delete("/{eleve_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_eleve_route(eleve_id: int, db: db_dependancy):
    delete_eleve(db, eleve_id)
    return None
