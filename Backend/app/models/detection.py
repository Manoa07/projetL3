from sqlalchemy import Column, ForeignKey, Integer, String
from DB.database import Base


class Detection(Base):
    __tablename__ = "detection"
    id_detection = Column(Integer, primary_key=True, autoincrement=True)
    type_detection = Column(String(80), nullable=False)
    id_capture_capture = Column(Integer, ForeignKey("image_capture.id_capture"), nullable=False)
    id_eleve_eleve = Column(Integer, ForeignKey("eleve.Id_eleve"), nullable=False)
