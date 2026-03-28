# Importing Libraries
from pydantic import BaseModel
from typing import Any, Optional

# Initializing
class BaseResponseModel(BaseModel):
    data: Optional[Any] = None
    message: Optional[str] = None


class BaseErrorModel(BaseModel):
    message: Optional[str] = None
