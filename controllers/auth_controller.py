# controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import or_
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from config.db_config import get_db, db_dependency
from helper.token_helper import TokenHelper
from models.users_table import Users
from dtos.auth_models import LoginRequest, OTPRequest, UserModel
from helper.api_helper import *
import random
from helper.email_helper import EmailHelper
from helper.hashing import *


class AuthController:
    def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
        try:
            validated_data = LoginRequest(
                username=form_data.username, 
                password=form_data.password
            )
            validated_username = validated_data.username
        except ValidationError:
            APIHelper.send_unauthorized_error(errorMessageKey="translations.INVALID_CREDENTIALS")

        user = db.query(Users).filter(
            or_(
                Users.email == validated_username,
                Users.phoneNumber == validated_username
            )
        ).first()

        if not user:
            return APIHelper.send_error_response(errorMessageKey="translations.INVALID_CREDENTIALS")
        
        if not Hash.verify(form_data.password, user.hashedPassword):
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.UNAUTHORIZED")
        
        otp_code = str(random.randint(1000, 9999))
        user.otp = otp_code
        user.otpExp = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        db.commit()

        if not EmailHelper.send_otp_email(user.email, otp_code):
            return APIHelper.send_error_response(errorMessageKey="translations.SEND_FAILED")
                
        token = TokenHelper.create_access_token(user.userName, user.id, user.roleId, timedelta(days=20))
        
        # return {'access_token': token, 'token_type': 'bearer','email': user.email}  
        response_data = {
            'access_token': token, 
            'token_type': 'bearer',
            'email': user.email
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.LOGIN_SUCCESS"
        )
    
    def verify_otp( otp: OTPRequest, db: db_dependency, user: Annotated[dict, Depends(TokenHelper.get_current_user)]):  
        
        user = db.query(Users).filter(Users.id == user.get("id")).first()
        if not user or user.otp != otp.OTP:
               return APIHelper.send_error_response(errorMessageKey="translations.INVALID_OTP")
        
        if datetime.now(timezone.utc) > user.otpExp.replace(tzinfo=timezone.utc):
            return APIHelper.send_error_response(errorMessageKey="translations.OTP_EXPIRE")
       
        user.otp = None
        user.otpExp = None
        db.commit()
        token = TokenHelper.create_access_token(user.userName, user.id, user.roleId, timedelta(days=30))
        
        response_data = {
            'access_token': token, 
            'token_type': 'bearer',
            'email': user.email
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.OPT_SENT"
        )