from typing import Optional
from pydantic import BaseModel, Field
from dtos.auth_models import UserModel
from helper.validation_helper import ValidationHelper
from enum import Enum


class SizeDetails(BaseModel):
    small_size_stock: int = 0
    medium_size_stock: int = 0
    large_size_stock: int = 0

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_name: str
    imageUrl: Optional[str] = None
    isTrending: bool = False
    discountPercentage: Optional[float] = None
    averageRating: Optional[float] = None
    # Nested size information
    small_size_stock:int
    medium_size_stock:int
    large_size_stock:int
    extra_large_size_stock:int

class ProductFilterParams(BaseModel):
    category_name: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    min_discount: Optional[float] = None # Percentage (e.g., 20 for 20% off)

class ProductReview(BaseModel):
    product_id: int = Field(...,ge=1)
    comment: Optional[str] = Field(None, max_length=500)
    rating: float = Field(None, ge=0, le=5)  # Rating between 0 and 5


class ProductSort(str, Enum):
    PRICE_LOW = "price_low"
    PRICE_HIGH = "price_high"
    NAME_ASC = "name_asc"

class ProductTrending(str,Enum):
    true="true"

