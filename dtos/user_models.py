from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from pydantic_extra_types.phone_numbers import PhoneNumber

class ChangePasswordModel(BaseModel):
    oldPassword: str= Field(max_length=72, min_length=8)
    newPassword: str= Field(max_length=72, min_length=8)

class ForgotPasswordModel(BaseModel):
    email: EmailStr

class ResetPasswordModel(BaseModel):
    password: str= Field(max_length=72, min_length=8)

class PaymentDetailModel(BaseModel):
    credit_card_number: str = Field(..., pattern=r"^\d{16}$")
    card_expiry: str = Field(..., pattern=r"^(0[1-9]|1[0-2])\/?([0-9]{2})$") # MM/YY format
    card_cvv: str= Field(..., pattern=r"^\d{3}$")
class UpdateEmailRequestModel(BaseModel):
    email: EmailStr

class UpdatePhoneNumberRequestModel(BaseModel):
    phone_number :  PhoneNumber

class UpdateUserRequest(BaseModel):
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
