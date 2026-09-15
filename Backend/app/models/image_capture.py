from sqlalchemy import Column, Date, Integer, String, Time
from DB.database import Base


class ImageCapture(Base):
    __tablename__ = "image_capture"
    id_capture = Column(Integer, primary_key=True, autoincrement=True)
    fichier_capture = Column(String, nullable=False)
    date_capture = Column(Date, nullable=False)
    heure_capture = Column(Time, nullable=False)
