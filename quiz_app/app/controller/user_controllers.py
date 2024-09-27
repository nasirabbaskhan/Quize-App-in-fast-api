from datetime import timedelta
from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from app.controller.auth_controller import generateAccessAndRefreshToken, generateToken, generateDecodedToken, passwordIntoHash, varifyPassword
from app.db.db_connector import get_session
from app.model.user_models import CreateUser, LoginUser, Token, User
from app.utils.exceptions import ConflictException, InvalidInputException, NotFoundException
from app.setting import access_expiry_time, refresh_expiry_time
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

auth_schema= OAuth2PasswordBearer(tokenUrl= "/token")



# user signup functionality
def signupFn(user_form:CreateUser, session:Annotated[Session, Depends(get_session)]):
    #1: verify user's email or password exist or not 
    users= session.exec(select(User)) # get all users to varfy each user
    for user in users:
        is_email_exist= user.user_email==user_form.user_email
        is_password_exist= varifyPassword(user_form.user_password, user.user_password)
        if is_email_exist and is_password_exist:
            raise ConflictException("email and password")
            # raise HTTPException(status_code=404, detail="email and password alreay exist")
        elif is_email_exist:
            raise ConflictException("email")
        elif is_password_exist:
            raise ConflictException("password")
        
       
    #2: adding the users signup data into database if user's email or password not exist 
   
    #convert the plan password into has password
    hashed_password= passwordIntoHash(user_form.user_password)
    #set the user name, email and hash password into User model
    user= User(user_name=user_form.user_name, user_email=user_form.user_email, user_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

   # Generate access and refresh tokens for the new user
    data = {
        "user_name": user.user_name,
        "user_email": user.user_email,
        "access_expiry_time": access_expiry_time,
        "refresh_expiry_time": refresh_expiry_time
    }
    # print(data)
    tokens_data = generateAccessAndRefreshToken(data)
    
    refresh_token= tokens_data["refresh_token"]["token"]
    
    # set refresh_token in Token table  and add it to database for generate the access_token when needed
    token= Token(refresh_token=refresh_token, user_id=user.user_id)
    print("nasir user", user.user_id)
    session.add(token)
    session.commit()
    return tokens_data
    
    
    
    

# user login functionality
"""
def login(login_form:LoginUser,session:Session):
def login(login_form:OAuth2PasswordRequestForm,session:Session)

LoginUser model and OAuth2PasswordRequestForm are same and use for same purpose

LoginUser model is made by developers that inforse to enter only email and passwor in login_form

class LoginUser(BaseModel):
    user_email:str
    user_password:str

BUT OAuth2PasswordRequestForm model is comes from fastapi.security that is prebuild and use for inforse to enter 
only email and passwor in login_form that it>

"""


def loginFn(login_form:LoginUser,session:Annotated[Session, Depends(get_session)]):
    #1: verify user's email or password exist or not 
    users= session.exec(select(User)) # get all users to varfy each user
    for user in users:
        is_email_exist= user.user_email== login_form.user_email
        is_password_exist= varifyPassword(login_form.user_password, user.user_password)
        if is_email_exist and is_password_exist:
            #2: if both exist then Generate the Aceess token and refresh token
        
            data = {
                "user_name": user.user_name,
                "user_email": user.user_email,
                "access_expiry_time": access_expiry_time,
                "refresh_expiry_time": refresh_expiry_time
            }
            tokens_data = generateAccessAndRefreshToken(data)
            
            refresh_token= tokens_data["refresh_token"]["token"]
                        
            
            # update te refresh token in database that was created in at signup time
            token = session.exec(select(Token).where(Token.user_id==user.user_id)).first()
            
            if token is None:
                raise HTTPException(status_code=404, detail="Token not found for the given user")
            token.refresh_token= refresh_token
            session.add(token)
            session.commit()
            session.refresh(token)
            return tokens_data
    else:
        raise InvalidInputException("Email or Password")  
        


# userget funtionality
"""
We have get the token from user to varify the email that is enoded in token is exist in dabase or not
for that we have need to first decode the token to get email of user for varifying and at the end we well return the user credential 

the returning data have the decodedData that was encoded
data= {
            "user_name": user.user_name,
            "user_email": user.user_email,
            "exp": expire
        }
we have need to get email than 

email= data["user_email"]
"""

def getUser(token:Annotated[str, Depends(auth_schema)], session:Annotated[Session,Depends(get_session)]):
    try:
        if token:
            data= generateDecodedToken(token)
            user_email= data["user_name"]
            user=session.exec(select(User).where(User.user_email==user_email)).one() # get the user that having the user email
            return user
    except:
        raise NotFoundException("Token")
    
    


def tokenService(refresh_token:str, session:Annotated[Session, Depends(get_session)]):
    if refresh_token:
        # varify refresh token exist in db
        db_refres_token=session.exec(select(Token).where(Token.refresh_token==refresh_token)).one()
        if not db_refres_token:
            raise HTTPException(status_code=404, detail="refresh token is not in db")
        # return db_refres_token
        #db_refres_token= {
        # "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJsdWxpIiwidXNlcl9lbWFpbCI6Imx1bGlAZ21haWwuY29tIiwiZXhwIjoxNzI1OTUxMDY0fQ.k3WF11gnjzoNP86xX5jgm9iVvV9kuykKMnRoRVwSF84",
        # "user_id": 23,
        # "token_id": "455fdfcc-2165-455f-8ca6-444baea273cc"
        # }
        
        # getting refresh token fr
        token_refresh= db_refres_token.refresh_token
        
        # decode the refresh token
        decoded_token_refresh=generateDecodedToken(token_refresh)
        decoded_user_email= decoded_token_refresh["user_email"]
        
       
        # get user information
        user_data=session.exec(select(User).where(User.user_email==decoded_user_email)).first()
        
        # generate access_token
        if  user_data is not None:
            user_email= user_data.user_email
            user_name= user_data.user_name
        data= { 
               "user_email": user_email,
               "user_name":user_name 
               }
        
        expiry_time= timedelta(minutes=30)
        new_eccess_token=generateToken(data=data, expiry_time=expiry_time)
        return new_eccess_token
       
    else:
        raise HTTPException(status_code=404, detail="refresh token is missing")