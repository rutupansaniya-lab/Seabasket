# Importing Libraries
from pydantic import BaseModel, Field, model_validator
from typing import Any, Literal, Optional, Union
from enum import Enum

class CartAction(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    REMOVE="remove"

class SizeEnum(str, Enum):
    S = "S"
    M = "M"
    L = "L"
    
# Initializing
class CartItemModel(BaseModel):
    productId: int = Field(gt=0)
    quantity: int = Field(gt=0)
    size: SizeEnum


class CartUpdateModel(BaseModel):
    action: Optional[CartAction] = Field(None)
    quantity: Optional[int] = Field(None, ge=0)

    @model_validator(mode='after')
    def check_either_or(self):
        # Case 1: Both are None
        if self.action is None and self.quantity is None:
            raise ValueError("You must provide either 'action' or 'quantity'.")
        
        # Case 2: Both are provided
        if self.action is not None and self.quantity is not None:
            raise ValueError("Provide 'action' OR 'quantity', not both.")
            
        return self

    