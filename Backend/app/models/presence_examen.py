from sqlalchemy import Column, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from DB.database import Base


class PresenceExamen(Base):
    __tablename__ = "presence_examen"
    id_presence_examen = Column(Integer, primary_key=True, autoincrement=True)
    status_presence_examen = Column(String(50), nullable=False)
    heure_arrive_examen = Column(Time, nullable=True)
    id_eleve_eleve = Column(Integer, ForeignKey("eleve.Id_eleve"), nullable=False)
    id_examen_examen = Column(Integer, ForeignKey("examen.id_examen"), nullable=False)
    eleve = relationship("Eleve", back_populates="presence_examen")
    examen = relationship("Examen", back_populates="presence_examen")
