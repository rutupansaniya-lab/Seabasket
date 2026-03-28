# Importing libraries
from typing import Annotated

from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime, timedelta, timezone
from dtos.auth_models import UserModel
from helper.api_helper import APIHelper
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from utils.db_helper import DBHelper

# JWT Configuration

"""Please generate a new JWT_SECRET `using openssl rand -hex 32` command and add it in the .env file"""

# Initializing the Hashing alogorith
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


class TokenHelper:
    def create_access_token(username: str, user_id: int, role_id: int, expires_delta: timedelta):
        encode = {'sub': username, 'id': user_id, 'role': role_id}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({'exp': expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


    def verify_token(token: str) -> UserModel:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("id")
            if user_id is None:
                return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        except JWTError:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        user = DBHelper.get_user_by_id(user_id)
        if user is None:
            return APIHelper.send_unauthorized_error(
                errorMessageKey='translations.UNAUTHORIZED')
        return UserModel(**user._mapping)


    async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
        try:    
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get('sub')
            user_id: int = payload.get('id')
            role_id: int = payload.get('role')

            if username is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate user credentials"
                )

        except ExpiredSignatureError:
            # Catches specifically expired tokens
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            # Catches other token issues (malformed, bad signature, etc.)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
        )

        return {
            'username': username,
            'id': user_id,
            'role': role_id
        }
     
     
    

