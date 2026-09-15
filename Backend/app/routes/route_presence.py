from typing import List
import cv2
from fastapi import APIRouter, File, Form, UploadFile
import numpy as np
from DB.database import db_dependancy
from schema.sch_presence import Create_presence, Presence_eleve
from services.presence_service import create_presence, get_presence_all, get_presence
from modules.presence import SystemePresence

router = APIRouter(prefix="/presence", tags=["Presence"])

# Correction : au lieu de recréer SystemePresence à chaque requête (ce qui
# recharge la base des embeddings à chaque image), on conserve l'instance en
# cache de module. Elle est réutilisée tant que l'id_cours ne change pas.
# Dès qu'une requête arrive avec un id_cours différent, on recrée l'instance
# pour recharger la base et réinitialiser l'état des présences du jour.
_systeme_cache: SystemePresence | None = None
_cache_id_cours: int | None = None


def _get_systeme(id_cours: int, db) -> SystemePresence:
    global _systeme_cache, _cache_id_cours
    if _systeme_cache is None or _cache_id_cours != id_cours:
        _systeme_cache = SystemePresence(id_cours, db, seuil_distance=0.8)
        _cache_id_cours = id_cours
    return _systeme_cache


@router.post("/create")
def create_presence_route(presence: Create_presence, db: db_dependancy):
    return create_presence(presence, db)


@router.get("/eleve/{eleve_id}", response_model=List[Presence_eleve])
def get_presence_all_route(eleve_id: int, db: db_dependancy):
    return get_presence_all(eleve_id, db)


@router.get("/eleve_last/{eleve_id}", response_model=Presence_eleve)
def get_presence_route(eleve_id: int, db: db_dependancy):
    return get_presence(eleve_id, db)


@router.post("/detecter")
async def detect(db: db_dependancy, id_cours: int = Form(...), file: UploadFile = File(...)):
    # Correction : on réutilise l'instance en cache plutôt que d'en créer une
    # nouvelle à chaque appel, ce qui évite le rechargement des embeddings.
    systeme = _get_systeme(id_cours, db)
    contents = await file.read()
    frame = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    resultats = systeme.traiter_image(frame)
    return {"resultats": resultats}
