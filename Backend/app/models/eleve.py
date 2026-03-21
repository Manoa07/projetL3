from DB.database import Base
from sqlalchemy import Integer, Column, LargeBinary,String
from sqlalchemy.orm import relationship

class Eleve(Base):
    __tablename__= 'eleve'
    Id_eleve=Column(Integer,primary_key=True,unique=True,autoincrement=True,index =True)
    Nom_eleve=Column(String(100),nullable=False)
    Prenom_eleve=Column(String(100),nullable=False)
    Classe_eleve=Column(String(50),nullable=False)
    Numero_eleve=Column(Integer,unique=True,nullable=False)
    photo_eleve=Column(String,nullable=True)
    embedding=Column(LargeBinary , nullable=True)
    presence=relationship("Presence", back_populates="eleve")
    surveillance=relationship("Surveillance",back_populates="eleve")
