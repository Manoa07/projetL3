from DB.database import Base
from sqlalchemy import Integer, Column,String,Date,Time,ForeignKey
from sqlalchemy.orm import relationship

class Cours(Base):
    __tablename__= 'cours'
    Id_cours=Column(Integer,primary_key=True,autoincrement=True, index=True)
    Nom_cours=Column(String)
    Professeur_cours=Column(String)
    Salle_cours=Column(String)
    # Références séparées conformément au MLD (les anciens champs restent
    # tolérés pour ne pas casser les données déjà présentes).
    date_cours=Column(Date, nullable=True)
    heure_debut_cours=Column(Time, nullable=True)
    heure_fin_cours=Column(Time, nullable=True)
    id_professeur_professeur=Column(Integer, ForeignKey("professeur.id_professeur"), nullable=True)
    id_salle_salle=Column(Integer, ForeignKey("salle.id_salle"), nullable=True)
    id_matiere_matiere=Column(Integer, ForeignKey("matiere.id_matiere"), nullable=True)
    presence =relationship("Presence",back_populates="cours")
    examen=relationship("Examen",back_populates="cours")
