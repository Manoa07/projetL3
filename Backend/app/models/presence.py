from DB.database import Base
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey,Date


class Presence(Base):
    __tablename__= 'presence'
    id_presence=Column(Integer,Primary_key=True,autoincrement=True,index=True)
    id_cours=Column(Integer,ForeignKey=True)
    id_eleve=Column(Integer,ForeignKey=True)
    Status_presence=Column(String)
    Heure_Presence=Column(Date)
