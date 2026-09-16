import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.camera import Camera


logger = logging.getLogger(__name__)


def create_camera(db: Session, camera_data):
	db_camera = Camera(
		Id_surveillance=camera_data.id_surveillance,
		Fichier_capture=camera_data.fichier_capture,
	)
	try:
		db.add(db_camera)
		db.commit()
		db.refresh(db_camera)
		return db_camera
	except IntegrityError as error:
		db.rollback()
		logger.error("Erreur d'intégrité lors de la création de la capture", exc_info=error)
		raise HTTPException(status_code=409, detail="Conflit de données.") from error
	except Exception as error:
		db.rollback()
		logger.error("Erreur lors de la création de la capture", exc_info=error)
		raise HTTPException(status_code=500, detail="Erreur interne.") from error


def get_all_cameras(db: Session):
	return db.query(Camera).all()
