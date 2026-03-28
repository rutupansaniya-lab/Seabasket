# controllers/admin_controller.py
import base64
import io
import os
from fastapi import HTTPException
from sqlalchemy import func
from helper.api_helper import APIHelper
from models.users_table import Users
from models.products_table import Products
from models.cetegories_table import Categories
from PIL import Image as PILImage 
from sqlalchemy import func

class AdminController:

    def all_users(db,user):
        if user.get('role') != 2 :
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")
        return db.query(Users).all()

    @staticmethod
    def admin_add_product(product_data, db, user):
        if user.get('role') != 2 :
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")
        # 1. Category Search Logic
        clean_input = product_data.category_name.replace(" ", "").replace("-", "").lower()
        category = db.query(Categories).filter(
            func.replace(func.replace(Categories.name, " ", ""), "-", "").ilike(f"%{clean_input}%")
        ).first()

        if not category:
            return APIHelper.send_not_found_error(errorMessageKey="translations.CATEGORY_NOT_FOUND")

        # 2. IMAGE PROCESSING (PILImage + 0.03MB target)
        try:
            # Check if file exists
            if not os.path.exists(product_data.imageUrl):
                return APIHelper.send_error_response(errorMessageKey="translations.FILE_PATH_NOT_FOUND")

            # Use PILImage instead of Image
            with PILImage.open(product_data.imageUrl) as img:
                # Convert to RGB (Required for JPEG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Resize to keep string short
                img.thumbnail((500, 500)) 

                # Compress to bytes
                buffer = io.BytesIO()
                # quality=50 and optimize=True usually hits exactly ~30KB (0.03MB)
                img.save(buffer, format="JPEG", quality=50, optimize=True)

                # Convert to Base64
                compressed_bytes = buffer.getvalue()
                base64_string = base64.b64encode(compressed_bytes).decode("utf-8")
                
                # Update the imageUrl inside product_data
                product_data.imageUrl = f"data:image/jpeg;base64,{base64_string}"

        except Exception as e:
            # This is where your previous error was caught
            return APIHelper.send_error_response(errorMessageKey="translations.IMAGE_PROCESSING_FAILED")
        # 3. SAVE PRODUCT
        new_product = Products(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            categoryId=category.id,
            imageUrl=product_data.imageUrl, # This is now the 0.05MB string
            isTrending=product_data.isTrending,
            discountPercentage=product_data.discountPercentage,
            averageRating=product_data.averageRating,
            small_size_stock=product_data.small_size_stock,
            medium_size_stock=product_data.medium_size_stock,
            large_size_stock=product_data.large_size_stock,
            extra_large_size_stock=product_data.extra_large_size_stock

        )
        db.add(new_product)
        db.flush()
        db.commit()

        return APIHelper.send_success_response(
            data={"product_id": new_product.id}, 
            successMessageKey="translations.PRODUCT_ADDED_SUCCESS"
        )

    def add_new_category(category_data, db,user):
        if user.get('role') != 2 :
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")
        existing_cat = db.query(Categories).filter(Categories.name.ilike(category_data.name)).first()
        if existing_cat:
            return APIHelper.send_error_response(errorMessageKey="translations.CATEGORY_EXISTS")

        new_category = Categories(name=category_data.name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return APIHelper.send_success_response(
            data={"id": new_category.id, "name": new_category.name}, 
            successMessageKey="translations.CATEGORY_ADDED_SUCCESS"
        )

    def update_category(category_id, category_data, db,user):
        if user.get('role') != 2 :
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")
        category = db.query(Categories).filter(Categories.id == category_id).first()
        if not category:
            return APIHelper.send_error_response(errorMessageKey="translations.CATEGORY_NOT_FOUND")
        
        existing_cat = db.query(Categories).filter(
            Categories.name.ilike(category_data.name),
            Categories.id != category_id
        ).first()
        
        if existing_cat:
            return APIHelper.send_error_response(errorMessageKey="translations.CATEGORY_EXISTS")

        category.name = category_data.name
        db.commit()
        db.refresh(category)
        return {"message": "Category updated successfully", "category": category}
   
    @staticmethod
    def update_or_get_product(product_id,db,user,name=None,description=None,price=None,category_name=None,imageUrl=None,isTrending=None,discountPercentage=None,averageRating=None,small_size_stock=None,medium_size_stock=None,large_size_stock=None,extra_large_size_stock=None):
    # 🔐 Optional: restrict to admin
        if user.get('role') != 2 :
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")

        # 1. Get product
        product = db.query(Products).filter(Products.id == product_id).first()

        if not product:
            return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")

        # 2. If no params passed → return product
        if all(v is None for v in [
            name, description, price, category_name, imageUrl,
            isTrending, discountPercentage, averageRating,
            small_size_stock, medium_size_stock,
            large_size_stock, extra_large_size_stock
        ]):
            return product

        # 3. Update fields dynamically
        if name is not None:
            product.name = name

        if description is not None:
            product.description = description

        if price is not None:
            product.price = price

        if isTrending is not None:
            product.isTrending = isTrending

        if discountPercentage is not None:
            product.discountPercentage = discountPercentage

        if averageRating is not None:
            product.averageRating = averageRating

        # ✅ Stock update
        if small_size_stock is not None:
            product.small_size_stock = small_size_stock

        if medium_size_stock is not None:
            product.medium_size_stock = medium_size_stock

        if large_size_stock is not None:
            product.large_size_stock = large_size_stock

        if extra_large_size_stock is not None:
            product.extra_large_size_stock = extra_large_size_stock

        # ✅ Category update
        if category_name is not None:
            clean_input = category_name.replace(" ", "").replace("-", "").lower()

            category = db.query(Categories).filter(
                func.replace(func.replace(Categories.name, " ", ""), "-", "").ilike(f"%{clean_input}%")
            ).first()

            if not category:
                return APIHelper.send_error_response(errorMessageKey="translations.CATEGORY_NOT_FOUND")

            product.categoryId = category.id
            
            if imageUrl is not None:
                try:
                    if not os.path.exists(imageUrl):
                        raise HTTPException(stauts_code=400, detail="Image path not found")

                    with PILImage.open(imageUrl) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")

                        img.thumbnail((500, 500))

                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=50, optimize=True)

                        base64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

                        product.imageUrl = f"data:image/jpeg;base64,{base64_string}"

                except Exception as e:
                    raise HTTPException(400, f"Image processing failed: {str(e)}")     
                   # 4. Save changes
        
        db.commit()
        db.refresh(product)

        return {
            "message": "Product updated successfully",
            "product": product
        }  

    def delete(db, user, product_id=None, category_id=None):
        # 🔐 ADMIN CHECK
        if user.get("role") != 2:
            return APIHelper.send_unauthorized_error(errorMessageKey="translations.ADMIN_ACCESS_REQUIRED")

        # --- 🚨 SAFETY CHECK: Prevent "Double Delete" Confusion ---
        if product_id and category_id:
            return APIHelper.send_error_response(errorMessageKey="translations.PROVIDE_ONLY_ONE_ID")

        # --- CASE 1: DELETE SINGLE PRODUCT ---
        if product_id:
            product = db.query(Products).filter(Products.id == product_id).first()
            if not product:
                return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")
            
            db.delete(product)
            db.commit()
            return APIHelper.send_success_response(
                data={"product_id": product_id}, 
                successMessageKey="translations.PRODUCT_DELETED_SUCCESS"
            )

        # --- CASE 2: DELETE CATEGORY (+ ALL ITS PRODUCTS) ---
        if category_id:
            category = db.query(Categories).filter(Categories.id == category_id).first()
            if not category:
                return APIHelper.send_not_found_error(errorMessageKey="translations.CATEGORY_NOT_FOUND")

            # Count products before deleting for a better response
            product_count = db.query(Products).filter(Products.categoryId == category_id).count()

            # 1. Delete all products belonging to this category
            db.query(Products).filter(Products.categoryId == category_id).delete()
            
            # 2. Delete the category itself
            db.delete(category)
            
            db.commit()
            return APIHelper.send_success_response(
                data={"category_id": category_id, "products_deleted": product_count}, 
                successMessageKey="translations.CATEGORY_DELETED_SUCCESS"
            )

        # --- CASE 3: NO ID PROVIDED ---
        return APIHelper.send_error_response(errorMessageKey="translations.MISSING_ID")