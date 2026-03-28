from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from config.db_config import db_dependency
from controllers.auth_controller import AuthController
from dtos.auth_models import OTPRequest
from helper.token_helper import TokenHelper
from helper.api_helper import *
from helper.hashing import *

auth = APIRouter(prefix="/auth", tags=["auth"])

@auth.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    return AuthController.login_for_access_token(form_data, db)

@auth.post("/verify-otp")
async def verify_otp( otp: OTPRequest, db: db_dependency, user: Annotated[dict, Depends(TokenHelper.get_current_user)]):  
    return AuthController.verify_otp(otp, db, user)

