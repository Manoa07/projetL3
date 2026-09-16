from fastapi import APIRouter, status

from DB.database import db_dependancy
from schema.sch_surveillance_examen import (
    SurveillanceExamenCreate,
    SurveillanceExamenResponse,
)
from services import surveillance_examen_service


router = APIRouter(prefix="/surveillance-examen", tags=["Surveillance Examen"])


@router.post("/", response_model=SurveillanceExamenResponse, status_code=status.HTTP_201_CREATED)
def create_surveillance_examen(data: SurveillanceExamenCreate, db: db_dependancy):
    return surveillance_examen_service.create_surveillance_examen(db, data)


@router.get("/{surveillance_id}", response_model=SurveillanceExamenResponse)
def get_surveillance_examen(surveillance_id: int, db: db_dependancy):
    return surveillance_examen_service.get_surveillance_examen(db, surveillance_id)


@router.get("/", response_model=list[SurveillanceExamenResponse])
def get_surveillance_examen_list(
    db: db_dependancy,
    skip: int = 0,
    limit: int = 100,
):
    return surveillance_examen_service.get_all_surveillances_examen(db, skip, limit)


@router.put("/{surveillance_id}", response_model=SurveillanceExamenResponse)
def update_surveillance_examen(
    surveillance_id: int,
    data: SurveillanceExamenCreate,
    db: db_dependancy,
):
    return surveillance_examen_service.update_surveillance_examen(
        db,
        surveillance_id,
        data,
    )


@router.delete("/{surveillance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surveillance_examen(surveillance_id: int, db: db_dependancy):
    surveillance_examen_service.delete_surveillance_examen(db, surveillance_id)
