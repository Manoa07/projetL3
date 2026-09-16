from sqlalchemy import Column, Date, Integer, String, Time
from sqlalchemy.orm import relationship
from DB.database import Base


class ImageCapture(Base):
    __tablename__ = "image_capture"
    id_capture = Column(Integer, primary_key=True, autoincrement=True)
    fichier_capture = Column(String, nullable=False)
    date_capture = Column(Date, nullable=False)
    heure_capture = Column(Time, nullable=False)
    detections = relationship("Detection", back_populates="image_capture")
    surveillance_examens = relationship("SurveillanceExamen", back_populates="image_capture")
