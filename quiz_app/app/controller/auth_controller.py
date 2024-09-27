from typing import Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.setting import access_expiry_time, refresh_expiry_time,algorithm,secret_key,expiry_time_str
from datetime import datetime ,timedelta, timezone




# SECRET = 'secret key'
# ALGORITHM = "HS256"
# EXPIRY_TIME= 20
def generateToken(data:dict, expiry_time:timedelta): # this method used for both access_token and refresh_token generation
    try:
       
        to_encoded_data= data.copy() # we want to add expiry time in user provided data so we have copy it to adding expiry time 
    
        to_encoded_data.update({
           "exp": datetime.utcnow() + access_expiry_time  # current dateTime + access_expiry_time
           
        })
        
        print("to_encoded_data", to_encoded_data)
       
        token= jwt.encode(to_encoded_data ,secret_key, algorithm = algorithm ) #secret_key ,algorithm comes from env->setting with timedelta
        
        
        return token
    except JWTError as je:
        print("JWT ERROR", je)
        
        
def generateDecodedToken(token:str):
    try:
        
        decodedToken=jwt.decode(token,secret_key, algorithms = algorithm)

        return decodedToken
       
    except JWTError as je:
        print("after jwt error",je)

        return je
 
 
# generat the hash password
pwd_context= CryptContext(schemes="bcrypt") 
  
def passwordIntoHash(plaintext:str):
    hash_pasword= pwd_context.hash(plaintext)
    return hash_pasword
    
    

    
# varify the user pasword is exist or not in database
def varifyPassword(plaintext, hash_passsword):
    return pwd_context.verify(plaintext, hash=hash_passsword)



    
def generate_admin_token(data: dict, expires_delta: timedelta) -> str:
    """
    Generate an admin token.

    Args:
        data (dict): Admin data to be encoded.
        expires_delta (timedelta): Expiry time for the token.

    Returns:
        str: Generated admin token.
    """
    # Make a copy of the admin data
    to_encode = data.copy()
    print("admin", data)
    
    # Calculate the expiry time
    expire = datetime.now(timezone.utc) + expires_delta
    
    # Update the data with the expiry time
    to_encode.update({"exp": expire})
    
    # Encode the data to generate the token
    access_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    
    
    
    
    return access_token

def generateAccessAndRefreshToken(user_details: dict[str, Any]):
    """
    Generates access and refresh tokens for a user.

    Args:
        user_details (dict): A dictionary containing user details.

    Returns:
        dict: A dictionary containing the generated access and refresh tokens.
    """
    print("User details in generate eccess an drefresh token funtion", user_details)
    # Constructing data payload for tokens
    data = {
        "user_name": user_details["user_name"],
        "user_email": user_details["user_email"]
    }
    # Generate access and refresh tokens
    access_token = generateToken(data, user_details["access_expiry_time"].total_seconds())
    refresh_token = generateToken(data, user_details["refresh_expiry_time"].total_seconds())
    access_expiry_time = user_details["access_expiry_time"]
    refresh_expiry_time = user_details["refresh_expiry_time"]

    return {
        "access_token": {
            "token": access_token,
            "access_expiry_time": access_expiry_time
        },
        "refresh_token": {
            "token": refresh_token,
            "refresh_expiry_time": refresh_expiry_time
        }
    }

    

 