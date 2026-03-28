
# routes/orders.py
from fastapi import APIRouter, Depends, status
from typing import Annotated, Optional
from config.db_config import db_dependency
from helper.token_helper import TokenHelper
from controllers.order_controller import OrderController
from routes.users import user_dependency

orders = APIRouter(tags=['orders'], prefix='/orders')

@orders.get("/{order_id}/status")
async def track_status(order_id: int, db: db_dependency, current_user: user_dependency):
    return OrderController.track_order_status(order_id, db, current_user)

@orders.patch("/{order_id}/cancel")
async def cancel_order(order_id: int, db: db_dependency, current_user: user_dependency):
    return OrderController.cancel_order(order_id, db, current_user)

@orders.get("/user/my-orders") 
def show_my_orders(
    db: db_dependency,
    user: user_dependency,
    order_id: Optional[int] = None  
):
    return OrderController.get_order_history(db=db, current_user=user, order_id=order_id)