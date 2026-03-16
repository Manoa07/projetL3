from DB.database import Base
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey


class Eleve(Base):
    __tablename__= 'eleve'
    Id_eleve=Column(Integer,primary_key=True,autoincrement=True,index =True)
    Nom_eleve=Column(String)
    Prenom_eleve=Column(String)
    Classe_eleve=Column(String)
    Numero=Column(Integer)
