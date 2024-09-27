from starlette.config import Config
from starlette.datastructures import Secret

from datetime import timedelta 

try: 
    config = Config(".env")
    
except FileNotFoundError:
    config = Config()
    
DATABASE_URL= config("DATABASE_URL", cast=Secret)

expiry_time_str = config.get("ACCESS_EXPIRY_TIME")
access_expiry_time= timedelta(minutes=int(expiry_time_str)) # timedalta convert into minuts

refresh_time_str = config.get("REFRESH_EXPIRY_TIME")
refresh_expiry_time= timedelta(days=int(refresh_time_str))  # timedalta convert into days
secret_key= config.get("SECRET_KEY")

algorithm= config.get("ALGORITHM")
