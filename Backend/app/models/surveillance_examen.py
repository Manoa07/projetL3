from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from DB.database import Base


class SurveillanceExamen(Base):
    __tablename__ = "surveillance_examen"
    id_surveillance = Column(Integer, primary_key=True, autoincrement=True)
    remarque_surveillance = Column(String, nullable=True)
    status_examen = Column(String(50), nullable=False)
    id_capture_capture = Column(Integer, ForeignKey("image_capture.id_capture"), nullable=True)
    id_examen_examen = Column(Integer, ForeignKey("examen.id_examen"), nullable=False)
    id_detection_detection = Column(Integer, ForeignKey("detection.id_detection"), nullable=True)
    image_capture = relationship("ImageCapture", back_populates="surveillance_examens")
    examen = relationship("Examen", back_populates="surveillance_examen")
    detection = relationship("Detection", back_populates="surveillance_examens")
