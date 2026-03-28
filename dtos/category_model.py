from typing import Optional
from pydantic import BaseModel, Field
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper



class CategoryCreate(BaseModel):
    name: str