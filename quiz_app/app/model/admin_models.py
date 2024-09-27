from sqlmodel import SQLModel, Field

class Admin(SQLModel, table=True):
    admin_id:int|None = Field(default=None, primary_key=True)
    admin_name:str
    admin_email:str
    admin_password:str
    
class AdminSignup(SQLModel):
    admin_name:str
    admin_email:str
    admin_password:str
    
    
class AdminLogin(SQLModel):
    admin_email:str
    admin_password:str
    
    
class AdminToken(SQLModel, table=True):
    """Model for admin token."""
    admin_tokenId: int | None = Field(None, primary_key=True)
    admin_token: str
    admin_id:int | None = Field(foreign_key="admin.admin_id")