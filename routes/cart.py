# routes/cart.py
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated, Optional
from config.db_config import db_dependency
from helper.token_helper import TokenHelper
from controllers.cart_controller import CartController
from dtos.cart_model import CartAction, CartItemModel, CartUpdateModel, SizeEnum

cart = APIRouter(tags=['cart'], prefix='/cart')

# Naming this user_dependency as you prefer
user_dependency = Annotated[dict, Depends(TokenHelper.get_current_user)]

@cart.post("/add-cart")
async def add_to_cart(cart_data: CartItemModel, db: db_dependency, current_user: user_dependency):
    return CartController.add_to_cart(cart_data, db, current_user)

@cart.patch("/") 
async def update_or_view_cart(
    db: db_dependency,
    user: user_dependency,
    # Now these stay as optional Query parameters
    cart_item_id: Optional[int] = Query(None),
    value: CartAction = Query(None)
):
    return await CartController.manage_cart_patch(
        db=db, 
        current_user=user, 
        cart_item_id=cart_item_id, 
        value=value
    )