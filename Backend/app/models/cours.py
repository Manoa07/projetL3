from DB.database import Base
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey,Date


class Cours(Base):
    __tablename__= 'cours'
    Id_cours=Column(Integer,primary_key=True,autoincrement=True, index=True)
    Nom_cours=Column(String)
    Professeur_cours=Column(String)
    Date_cours=Column(Date)
s