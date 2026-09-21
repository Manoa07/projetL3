from sqlalchemy import Column, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from DB.database import Base


class PresenceCours(Base):
    __tablename__ = "presence_cours"
    id_presence_cours = Column(Integer, primary_key=True, autoincrement=True)
    status_presence_cours = Column(String(50), nullable=False)
    heure_arrive_cours = Column(Time, nullable=False)
    heure_depart_cours = Column(Time, nullable=True)
    id_cours_cours = Column(Integer, ForeignKey("cours.Id_cours", ondelete="CASCADE"), nullable=False)
    id_eleve_eleve = Column(Integer, ForeignKey("eleve.Id_eleve", ondelete="CASCADE"), nullable=False)
    cours = relationship("Cours", back_populates="presence_cours")
    eleve = relationship("Eleve", back_populates="presence_cours")
