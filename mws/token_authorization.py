import jwt
from fastapi import Header, HTTPException, Depends
from app.config.settings import settings  

def authenticate_token(token , required_fields = []):
    try :
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        token_data = {}
        for field in required_fields:
            value = payload.get(field)

            if value is None:
                raise Exception("Value not found")

            token_data[field] = value
            
        return {"state" : True , "data" : token_data}
        
    except :
        return {"state" : False , "msg" : "token_not_valid"}
