# Importing Libraries
from pydantic import BaseModel
from typing import Any, Optional

# Initializing
class AddressModel(BaseModel):
    addressLine1: str
