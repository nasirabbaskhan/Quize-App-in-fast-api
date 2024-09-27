from sqlmodel import SQLModel, Session, create_engine
# from app.utils.imports import SQLModel, Session, create_engine, setting
from app import setting


connection_string :str = str(setting.DATABASE_URL).replace("postgresql", "postgresql+psycopg")
engine= create_engine(connection_string, connect_args={"sslmode":"require"}, pool_recycle=300, echo=True)

#create table
def create_table():
    SQLModel.metadata.create_all(engine)
    
    
#create session
def get_session():
    with Session(engine) as session:
        yield session