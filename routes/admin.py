# routes/admin.py
from fastapi import APIRouter, Depends, status
from typing import Annotated
from config.db_config import db_dependency
from helper.token_helper import TokenHelper
from controllers.admin_controller import AdminController
from dtos.category_model import CategoryCreate
from dtos.product_model import ProductCreate

admin = APIRouter(tags=['Admin'], prefix='/admin')
user_dependency = Annotated[dict, Depends(TokenHelper.get_current_user)]

@admin.get("/user")
async def all_users(db: db_dependency, user: user_dependency):
    return AdminController.all_users(db,user)

@admin.post("/add-product", status_code=status.HTTP_201_CREATED)
async def admin_add_product(product_data: ProductCreate, db: db_dependency, user: user_dependency):
    return AdminController.admin_add_product(product_data, db,user)

@admin.post("/category", status_code=status.HTTP_201_CREATED)
async def add_new_category(category_data: CategoryCreate, db: db_dependency, user: user_dependency):
    return AdminController.add_new_category(category_data, db,user)

@admin.put("/category/{category_id}")
async def update_category(category_id: int, category_data: CategoryCreate, db: db_dependency, user: user_dependency):
    return AdminController.update_category(category_id, category_data, db,user)

@admin.patch("/product/{product_id}")
def update_product(
    db: db_dependency,
    user: user_dependency,
    product_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    category_name: str = None,
    imageUrl: str = None,
    isTrending: bool = None,
    discountPercentage: float = None,
    averageRating: float = None,
    small_size_stock: int = None,
    medium_size_stock: int = None,
    large_size_stock: int = None,
    extra_large_size_stock: int = None
):
    # Use keyword arguments (name=name, etc.) to ensure data goes to the right place
    return AdminController.update_or_get_product(
        product_id=product_id,
        db=db,
        user=user,
        name=name,
        description=description,
        price=price,
        category_name=category_name,
        imageUrl=imageUrl,
        isTrending=isTrending,
        discountPercentage=discountPercentage,
        averageRating=averageRating,
        small_size_stock=small_size_stock,
        medium_size_stock=medium_size_stock,
        large_size_stock=large_size_stock,
        extra_large_size_stock=extra_large_size_stock
    )

@admin.delete("/delete")
async def product_category_delete(db:db_dependency,user:user_dependency,product_id:int=None,category_id:int=None):
    return AdminController.delete(db, user, product_id, category_id)