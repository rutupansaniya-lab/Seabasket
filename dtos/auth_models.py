from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, StringConstraints
from typing import Annotated, Union
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import literal

from config.constants import Constants


class UserModel(BaseModel): 
    userName: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr]
    phoneNumber: str
    hashedPassword: str = Field(max_length=72, min_length=8)

class Roles(BaseModel):
    id : Optional[int] = Field(ge=1, le=2, default=1)
    name : str
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    
class TokenModel(UserModel):
    access_token: str
    token_type: Optional[str] = 'Bearer'

LoginIdentifier = Union[
    EmailStr, 
    Annotated[str, StringConstraints(pattern=Constants.MOBILE_NUMBER_REGEX, strip_whitespace=True)]]

class LoginRequest(BaseModel):
    # This field will automatically accept an email OR a phone number
    username: LoginIdentifier
    password: str = Field(..., min_length=8, max_length=72)

class OTPRequest(BaseModel):
    OTP: str = Field(..., pattern=r'^\d{4}$')   