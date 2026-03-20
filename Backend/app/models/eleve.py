from DB.database import Base
from sqlalchemy import Integer, Column,String
from sqlalchemy.orm import relationship

class Eleve(Base):
    __tablename__= 'eleve'
    Id_eleve=Column(Integer,primary_key=True,unique=True,autoincrement=True,index =True)
    Nom_eleve=Column(String)
    Prenom_eleve=Column(String)
    Classe_eleve=Column(String)
    Numero_eleve=Column(Integer)
    presence=relationship("Presence", back_populates="eleve")
    surveillance=relationship("Surveillance",back_populates="eleve")
