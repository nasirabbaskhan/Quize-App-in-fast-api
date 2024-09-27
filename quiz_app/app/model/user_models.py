from pydantic import BaseModel
from sqlmodel import SQLModel, Field
import uuid

class User(SQLModel, table=True):
    __tablename__ ='user'  # Explicitly define the table name
    user_id:int|None= Field(default=None, primary_key=True)
    user_name:str
    user_email:str
    user_password:str
    
class CreateUser(SQLModel):
    user_name:str
    user_email:str
    user_password:str
    
class LoginUser(SQLModel):
    user_email:str
    user_password:str
    
    
class Token(SQLModel, table=True):
    __tablename__ ='token'  
    token_id:str= Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    refresh_token:str
    user_id:int= Field( foreign_key="user.user_id")

    



    