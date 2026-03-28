from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from requests import Session
from config.db_config import db_dependency, get_db
from dtos.user_models import PaymentDetailModel
from helper.api_helper import APIHelper
from helper.token_helper import TokenHelper
from models.users_table import Users
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
from models.sizes_table import ProductSizes
import stripe 
from os.path import join,dirname

dotenv_path = join(dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class PaymentController:
    def create_payment_intent(db, current_user):
        user_id = current_user["id"]

        # 1. Get Address
        user = db.query(Users).filter(
            Users.id == user_id
        ).first()

        address=user.address

        if not address or address.strip() == "":
            return APIHelper.send_not_found_error(errorMessageKey="translations.ADDRESS_NOT_FOUND")

        # 2. Get Cart
        cart_items = db.query(CartItem, Products).join(
            Products, CartItem.productId == Products.id
        ).filter(CartItem.userId == user_id).all()

        if not cart_items:
            return APIHelper.send_error_response(errorMessageKey="translations.CART_EMPTY")

        total = Decimal("0.00")
        shipping = Decimal("100.00")

        # ✅ SIZE MAP (ADD XL also)
        size_map = {
            "s": "small_size_stock",
            "m": "medium_size_stock",
            "l": "large_size_stock",
            "xl": "extra_large_size_stock"
        }

        for c_item, prod in cart_items:

            size_key = c_item.size.lower()

            if size_key not in size_map:
                return APIHelper.send_error_response(errorMessageKey="translations.INVALID_SIZE")

            col = size_map[size_key]

            current_stock = getattr(prod, col, 0)

            # ❌ Stock check
            if current_stock < c_item.quantity:
                return APIHelper.send_error_response(errorMessageKey="translations.SIZE_NOT_AVAILABLE")
            # ✅ Price calculation
            discount = Decimal(str(prod.discountPercentage or 0))
            price = Decimal(str(prod.price))
            final_price = price - (price * discount / 100)

            total += final_price * c_item.quantity

        final_amount = total + shipping

        # 4. Create Stripe PaymentIntent
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(final_amount * 100),  # paise
                currency="inr",
                metadata={
                    "user_id": user_id,
                    "address": address[:500]
                }
            )
        except Exception as e:
            return APIHelper.send_error_response(errorMessageKey="translations.STRIPE_ERROR")

        response_data = {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": float(final_amount)
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
        )
    
    def confirm_payment(payment_intent_id, db):
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status != "succeeded":
                return APIHelper.send_error_response(errorMessageKey="translations.PAYMENT_FAILED")

            # Extract IDs from Stripe's payload
            user_id = int(intent["metadata"]["user_id"])
            address = intent["metadata"].get("address")

            if not address:
                return APIHelper.send_not_found_error(errorMessageKey="translations.ADDRESS_NOT_FOUND")

            # 2. Prevent duplicate execution
            # Since we don't have an order to check yet, we check if the cart is empty.
            # If the cart is empty, we assume this intent was already processed.
            cart_items = db.query(CartItem, Products).join(
                Products, CartItem.productId == Products.id
            ).filter(CartItem.userId == user_id).all()

            if not cart_items:
                return APIHelper.send_success_response(
                    data=None, 
                    successMessageKey="translations.ORDER_ALREADY_PROCESSED"
                )

            # 3. Create the Master Order FIRST (Status: packing)
            # We need to recalculate the final amount to be safe
            total = Decimal("0.00")
            shipping = Decimal("100.00")
            
            for c_item, prod in cart_items:
                discount = Decimal(str(prod.discountPercentage or 0))
                price = Decimal(str(prod.price))
                total += (price - (price * discount / 100)) * c_item.quantity
                
            final_amount = total + shipping

            new_order = Orders(
                userId=user_id,
                shippingAddressId=address,
                totalAmount=float(final_amount),
                orderStatus="packing" # SET EXACTLY AS REQUESTED
            )
            db.add(new_order)
            db.flush() # This generates the new_order.id needed for the items below

            # 4. Process Items, Reduce Stock, and Create OrderItems
            size_map = {
                "s": "small_size_stock",
                "m": "medium_size_stock",
                "l": "large_size_stock",
                "xl": "extra_large_size_stock"
            }

            for c_item, prod in cart_items:

                size_key = c_item.size.lower()
                col = size_map.get(size_key)

                if not col:
                    db.rollback()
                    return APIHelper.send_error_response(errorMessageKey="translations.INVALID_SIZE")

                current_stock = getattr(prod, col, 0)

                # ❌ Double-check stock before reducing
                if current_stock < c_item.quantity:
                    db.rollback()
                    stripe.Refund.create(payment_intent=payment_intent_id)
                    return APIHelper.send_error_response(errorMessageKey="translations.STOCK_OUT_DURING_PAYMENT")

                # ✅ Reduce stock directly in Products table
                setattr(prod, col, current_stock - c_item.quantity)

                # Price calc
                discount = Decimal(str(prod.discountPercentage or 0))
                price = Decimal(str(prod.price))
                final_price = price - (price * discount / 100)

                db.add(OrderItems(
                    orderId=new_order.id,
                    productId=prod.id,
                    quantity=c_item.quantity
                ))

            # 5. Clear cart
            db.query(CartItem).filter(CartItem.userId == user_id).delete()

            # 6. Final Commit
            db.commit()

            return APIHelper.send_success_response(
                data={"order_id": new_order.id, "status": new_order.orderStatus}, 
                successMessageKey="translations.ORDER_PLACED_SUCCESS"
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback() 
            raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")