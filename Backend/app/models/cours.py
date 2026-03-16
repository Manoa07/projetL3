from DB.database import Base
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey,DateTime
from sqlalchemy.orm import relationship

class Cours(Base):
    __tablename__= 'cours'
    Id_cours=Column(Integer,primary_key=True,autoincrement=True, index=True)
    Nom_cours=Column(String)
    Professeur_cours=Column(String)
    Date_cours=Column(DateTime)
    Salle_cours=Column(String)
    presence =relationship("Presence",back_populates="cours")
