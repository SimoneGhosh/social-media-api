from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#postgresql://<username>:<password>@<ip-address/hostname>/<database_name>
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Generis2026@localhost/socialmediaapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()