# routes/user.py
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from requests import Session
from config.db_config import db_dependency, get_db
from controllers.payment_controller import PaymentController
from dtos.user_models import PaymentDetailModel
from helper.token_helper import TokenHelper
from routes.users import user_dependency
import os
from dotenv import load_dotenv  
from fastapi import HTTPException, status
from decimal import Decimal
from sqlalchemy import func
import stripe
from models.orders_table import Orders, OrderItems
from models.address_table import Address
from models.cart_table import CartItem
from models.products_table import Products

import stripe 

payment = APIRouter(tags=['payment'], prefix='/payment')

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@payment.post("/checkout")
def create_payment_intent(
    db: Session = Depends(get_db),
    current_user: dict = Depends(TokenHelper.get_current_user)
):
    return PaymentController.create_payment_intent(db,current_user)

@payment.post("/confirm-payment")
def confirm_payment(
    payment_intent_id: str,
    db: Session = Depends(get_db)
):
    return PaymentController.confirm_payment(payment_intent_id,db)