# controllers/order_controller.py
from fastapi import HTTPException, status
from decimal import Decimal
from sqlalchemy import func
import stripe
from helper.api_helper import APIHelper
from models.orders_table import Orders, OrderItems
from models.address_table import Address
from models.cart_table import CartItem
from models.products_table import Products
from models.sizes_table import ProductSizes

class OrderController:
    @staticmethod
    def track_order_status(order_id, db, current_user):
        user_id = current_user.get("id")
        order = db.query(Orders).filter(Orders.id == order_id, Orders.userId == user_id).first()

        if not order:
            return APIHelper.send_not_found_error(errorMessageKey="translations.ORDER_NOT_FOUND")

        response_data= {"order_id": order.id, "order_status": order.orderStatus}

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
            )

    def cancel_order(order_id, db, current_user):
        user_id = current_user.get("id")
        order_query = db.query(Orders).filter(Orders.id == order_id, Orders.userId == user_id)
        order = order_query.first()

        if not order:
            return APIHelper.send_not_found_error(errorMessageKey="translations.ORDER_NOT_FOUND")
        
        current_status = order.orderStatus.lower()
        if current_status in ["shipped", "delivered", "cancelled"]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.ORDER_CANNOT_BE_CANCELLED"
            )
        
        order_query.update({"orderStatus": "Cancelled"})
        db.commit()
        return APIHelper.send_success_response(successMessageKey="translations.SUCCESS")

    @staticmethod
    def get_order_history(db, current_user, order_id=None):
        user_id = current_user.get("id")

        # --- CASE 1: Specific Order Detail ---
        if order_id:
            order = db.query(Orders).filter(
                Orders.id == order_id, 
                Orders.userId == user_id
            ).first()

            if not order:
                return APIHelper.send_not_found_error(errorMessageKey="translations.ORDER_NOT_FOUND")

            items_raw = db.query(OrderItems, Products).join(
                Products, OrderItems.productId == Products.id
            ).filter(OrderItems.orderId == order_id).all()

            item_list = [{
                "product_id": item.productId,
                "product_name": product.name,
                "image": product.imageUrl,
                "quantity": item.quantity,
                "price_at_purchase": float(item.totalAmount / item.quantity) if item.quantity > 0 else 0,
                "item_total": float(item.totalAmount)
            } for item, product in items_raw]

            response_data = {
                "order_id": order.id,
                "status": order.orderStatus,
                "total_amount": float(order.totalAmount),
                "placed_at": order.createdAt.strftime("%d %b %Y, %I:%M %p") if order.createdAt else None,
                "items": item_list
            }
            
            return APIHelper.send_success_response(data=response_data, successMessageKey="translations.SUCCESS")

        # --- CASE 2: Full Order History ---
        else:
            orders = db.query(Orders).filter(Orders.userId == user_id).order_by(Orders.createdAt.desc()).all()

            if not orders:
                return APIHelper.send_success_response(data=[], successMessageKey="translations.SUCCESS")

            history = []
            for ord_obj in orders:
                # For history list, you might want just a summary or the first item's image
                history.append({
                    "order_id": ord_obj.id,
                    "status": ord_obj.orderStatus,
                    "total_amount": float(ord_obj.totalAmount),
                    "placed_at": ord_obj.createdAt.strftime("%d %b %Y, %I:%M %p") if ord_obj.createdAt else None,
                })

            return APIHelper.send_success_response(data=history, successMessageKey="translations.SUCCESS")
