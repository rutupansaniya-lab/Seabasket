# controllers/cart_controller.py
from fastapi import HTTPException, status
from decimal import Decimal
from dtos.cart_model import CartAction
from helper.api_helper import APIHelper
from models.cart_table import CartItem
from models.products_table import Products
from models.sizes_table import ProductSizes
from models.users_table import Users

class CartController:
    
    @staticmethod
    def add_to_cart(cart_data, db, current_user):
        user_id = current_user.get("id")

        # ✅ 1. Check product exists
        product = db.query(Products).filter(
            Products.id == cart_data.productId
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # ✅ 2. Size mapping
        size_map = {
            "s": "small_size_stock",
            "m": "medium_size_stock",
            "l": "large_size_stock",
            "xl": "extra_large_size_stock"
        }

        size_key = cart_data.size.lower()
        col = size_map.get(size_key)

        if not col:
            return APIHelper.send_error_response(errorMessageKey="translations.SIZE_NOT_AVAILABLE")

        available_stock = getattr(product, col, 0)

        if cart_data.quantity < 1:
            return APIHelper.send_error_response(errorMessageKey="translations.SIZE_NOT_AVAILABLE")

        if cart_data.quantity > available_stock:
            return APIHelper.send_error_response(errorMessageKey="translations.SIZE_NOT_AVAILABLE")

        existing_item = db.query(CartItem).filter(
            CartItem.userId == user_id,
            CartItem.productId == cart_data.productId,
            CartItem.size == cart_data.size.upper()
        ).first()

        if existing_item:
            return APIHelper.send_error_response(errorMessageKey="translations.SIZE_EXISTS_CART")

        new_item = CartItem(
            userId=user_id,
            productId=cart_data.productId,
            size=cart_data.size.upper(),
            quantity=cart_data.quantity
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        response_data= {
            "message": "Product added to cart successfully",
            "cart_item_id": new_item.id,
            "product_id": new_item.productId,
            "size": new_item.size,
            "quantity": new_item.quantity
        }
        
        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.ADD_CART"
        )
    
    async def manage_cart_patch(db, current_user, cart_item_id=None, value=None):
        user_id = current_user.get("id")

      
        if value and not cart_item_id:
             return APIHelper.send_error_response(errorMessageKey="translations.INVALID_ID")


    
        if cart_item_id and value:
            cart_item = db.query(CartItem).filter(
                CartItem.id == cart_item_id, 
                CartItem.userId == user_id
            ).first()
            
            if not cart_item:
                return APIHelper.send_error_response(errorMessageKey="translations.CART_ITEM_NOT_FOUND")

            if value == "remove":
                db.delete(cart_item)
                db.commit()
              
            
            elif value in ["increase", "decrease"]:
                target_qty = cart_item.quantity + 1 if value == "increase" else max(1, cart_item.quantity - 1)
                cart_item.quantity = target_qty
                db.commit()
            else:
                return APIHelper.send_error_response(errorMessageKey="translations.INVAILD_INPUT_FOR_CART_ITEM")

        if cart_item_id and not value:
            result = db.query(CartItem, Products).\
                join(Products, CartItem.productId == Products.id).\
                filter(CartItem.id == cart_item_id, CartItem.userId == user_id).first()
            
            if not result:
                return APIHelper.send_not_found_error(errorMessageKey="translations.CART_ITEM_NOT_FOUND")

            item, prod = result
            price = Decimal(str(prod.price or 0))
            disc = Decimal(str(prod.discountPercentage or 0))
            eff_price = price - (price * disc / 100)
            
            response_data= {
                "cart_item_id": item.id,
                "product_name": prod.name,
                "product_id":prod.id,
                "image": prod.imageUrl,
                "size": item.size,
                "effective_price": float(round(eff_price, 2)),
                "quantity": item.quantity,
                "item_subtotal": float(round(eff_price * item.quantity, 2))
            }

            return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
            )

        results = db.query(CartItem, Products).\
            join(Products, CartItem.productId == Products.id).\
            filter(CartItem.userId == user_id).all()

        user_data = db.query(Users).filter(Users.id == user_id).first()
        
        cart_list = []
        subtotal = Decimal("0.00")

        for item, prod in results:
            price = Decimal(str(prod.price or 0))
            disc = Decimal(str(prod.discountPercentage or 0))
            eff_price = price - (price * disc / 100)
            item_total = eff_price * item.quantity
            subtotal += item_total
            
            cart_list.append({
                "cart_item_id": item.id,
                "product_name": prod.name,
                "product_id":prod.id,
                "image": prod.imageUrl,
                "size": item.size,
                "effective_price": float(round(eff_price, 2)),
                "quantity": item.quantity,
                "item_subtotal": float(round(item_total, 2))
            })

        response_data= {
            "status": "success",
            "delivery_address": user_data.address ,
            "items": cart_list,
            "summary": {
                "subtotal": float(round(subtotal, 2)),
                "shipping": 100.0,
                "grand_total": float(round(subtotal + 100, 2))
            }
        }
    
        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
            )
        