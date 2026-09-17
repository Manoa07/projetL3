import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
<<<<<<< Updated upstream
from sqlalchemy.orm import Session, declarative_base, sessionmaker


database_file = Path(__file__).resolve()
env_candidates = [database_file.parent.parent.parent / ".env"]
if len(database_file.parents) > 3:
    env_candidates.append(database_file.parents[3] / ".env")

for env_file in env_candidates:
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
        break
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL doit être défini.")
if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
    raise RuntimeError("DATABASE_URL doit utiliser PostgreSQL.")

engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c client_encoding=UTF8"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
=======
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql://postgres:NyHartsAdmin@localhost:5432/surveillance"
>>>>>>> Stashed changes


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependancy= Annotated[Session,Depends(get_db)]