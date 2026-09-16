import os
from typing import Annotated
import os

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base

<<<<<<< Updated upstream
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL doit être défini avec une URL PostgreSQL "
        "(par exemple postgresql+psycopg2://user:password@localhost/dbname)."
    )
if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
    raise RuntimeError("DATABASE_URL doit utiliser PostgreSQL.")

engine = create_engine(DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
=======
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not defined. Set it in the .env file.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


>>>>>>> Stashed changes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
<<<<<<< Updated upstream
db_dependancy= Annotated[Session,Depends(get_db)]
=======


db_dependancy = Annotated[Session, Depends(get_db)]

>>>>>>> Stashed changes
