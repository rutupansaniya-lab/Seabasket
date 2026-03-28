# controllers/user_controller.py
from datetime import datetime, timedelta, timezone
import random

from fastapi import HTTPException, Query, status
from sqlalchemy import func, null
from dtos.user_models import ForgotPasswordModel
from helper.email_helper import EmailHelper
from helper.hashing import Hash
from helper.api_helper import APIHelper
from helper.token_helper import TokenHelper
from models.users_table import Users
from models.roles_table import Roles
from models.address_table import Address
from models.products_table import Products
from models.reviews_table import ProductReview

class UserController: 
    @staticmethod
    def create_user(db, user_data):

        existing_username = db.query(Users).filter(Users.userName == user_data.userName).first()
        if existing_username:
            return APIHelper.send_error_response(errorMessageKey="translations.EXISTED_EMAIL")
        
        existing_user_email =db.query(Users).filter(Users.email == user_data.email).first()
        if existing_user_email:
            return APIHelper.send_error_response(errorMessageKey="translations.EXISTED_USERNAME")
        
        existing_user_phone_number =db.query(Users).filter(Users.phoneNumber == user_data.phoneNumber).first()
        if existing_user_phone_number:
            return APIHelper.send_error_response(errorMessageKey="translations.EXISTED_PHONE_NUMBER")

        hashed_pwd = Hash.get_hash(user_data.hashedPassword)

        new_user = Users(
            userName=user_data.userName,
            email=user_data.email,
            phoneNumber=user_data.phoneNumber,
            hashedPassword=hashed_pwd
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        response_data = {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.userName  
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.REGISTER_SUCCESS"
        )
    

    def change_password(db, password_data, current_user):

        user_id = current_user.get('id')
        user = db.query(Users).filter(Users.id == user_id).first()
        
        if not Hash.verify(password_data.oldPassword, user.hashedPassword):
            raise HTTPException(status_code=401, detail="INCORRECT_CURRENT_PASSWORD")
            
        user.hashedPassword = Hash.get_hash(password_data.newPassword)
        db.commit()
        return APIHelper.send_success_response(successMessageKey="translations.CHANGE_PASSWORD")


    def add_review(db, review_data, current_user):
        user_id = current_user.get('id')
        product_id = review_data.product_id

        product = db.query(Products).filter(Products.id == product_id).first()
        
        if not product:
            APIHelper.send_error_response(successMessageKey="translations.PRODUCT_NOT_FOUND")
        
        # Optional: Check if user already reviewed this product
        existing = db.query(ProductReview).filter(
            ProductReview.productId == review_data.product_id,
            ProductReview.userId == user_id
        ).first()
        
        if existing:
            APIHelper.send_error_response(successMessageKey="translations.ALREADY_REVIEWED")

        new_review = ProductReview(
            productId=review_data.product_id,
            userId=user_id,
            rating=review_data.rating,
            comment=review_data.comment # <--- Save the comment
        )
        db.add(new_review)
        db.flush() 

        # Recalculate Average
        avg_rating = db.query(func.avg(ProductReview.rating)).filter(
            ProductReview.productId == review_data.product_id
        ).scalar()
        
        product = db.query(Products).filter(Products.id == review_data.product_id).first()
        product.averageRating = round(avg_rating, 1)
        
        db.commit()
        return {"message": "Review submitted successfully", "rating": product.averageRating}
    
    @staticmethod
    def manage_review_patch(db, current_user, product_id, rating, comment=None):
        user_id = current_user.get("id")

        # 1. Look for an existing review by this user for this product
        review = db.query(ProductReview).filter(
            ProductReview.productId == product_id,
            ProductReview.userId == user_id
        ).first()

        # --- PART A: UPDATE LOGIC (If data is provided) ---
        if rating is not None or comment is not None:
            if not review:
                raise HTTPException(status_code=404, detail="Review not found. Please create one first.")

            if rating is not None:
                review.rating = rating
            if comment is not None:
                review.comment = comment
            
            db.commit()

            # Recalculate Product Average Rating
            avg_val = db.query(func.avg(ProductReview.rating)).filter(
                ProductReview.productId == product_id
            ).scalar()
            
            product = db.query(Products).filter(Products.id == product_id).first()
            if product:
                product.averageRating = round(float(avg_val), 1)
                db.commit()

        # --- PART B: GET LOGIC (Always returns the current state) ---
        if not review:
            return []

        return {
            "status": "success",
            "review_id": review.id,
            "product_id": review.productId,
            "rating": review.rating,
            "comment": review.comment,
            "last_updated": review.updatedAt
        }
        

    def forgot_password(email_data, db):
        
        user = db.query(Users).filter(Users.email == email_data.email).first()
        
        if not user:
            return APIHelper.send_error_response(errorMessageKey="translations.NOT_EXISTED_EMAIL")

        otp_code = str(random.randint(1000, 9999))
        user.otp = otp_code
        user.otpExp = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        db.commit()

        if not EmailHelper.send_otp_email(user.email, otp_code):
            return APIHelper.send_error_response(errorMessageKey="translations.SEND_FAILED")
        
        token = TokenHelper.create_access_token(user.userName, user.id, user.roleId, timedelta(days=20))
        
        response_data = {
            'access_token': token, 
            'token_type': 'bearer',
            'email': user.email
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.OPT_SENT"
        )
    
    def reset_password(password_data, current_user,db):

        user_id = current_user.get('id')
        user = db.query(Users).filter(Users.id == user_id).first()

        user.hashedPassword = Hash.get_hash(password_data.password)
        db.commit()

        return APIHelper.send_success_response(successMessageKey="translations.CHANGE_PASSWORD")

    def update_user_service(current_user, request, db):
        
        user_id=current_user.get('id')
        user = db.query(Users).filter(
            Users.id == user_id,
            Users.isDeleted == False
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
# 1. Fetch the user being updated
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return APIHelper.send_not_found_error(errorMessageKey="translations.USER_NOT_FOUND")

        # 3. PHONE NUMBER UNIQUE CHECK
        if request.phoneNumber and request.phoneNumber != user.phoneNumber:
            phone_exists = db.query(Users).filter(
                Users.phoneNumber == request.phoneNumber,
                Users.id != user_id
            ).first()
            
            if phone_exists:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.EXISTED_PHONE_NUMBER"
                )

        if request.phoneNumber:
            user.phoneNumber = request.phoneNumber

        # Address update
        if request.address:
            user.address = request.address

        db.commit()
        db.refresh(user)

        
        response_data= {
            "message": "User updated successfully",
            "username": user.userName,
            "id": user.id,
            "email": user.email,
            "phoneNumber": user.phoneNumber,
            "address": user.address  
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
        )

    def manage_review(db, review_data, current_user):
        user_id = current_user.get('id')
        product_id = review_data.product_id

        # 1. Check if the product even exists first
        product = db.query(Products).filter(Products.id == product_id).first()
        if not product:
            return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")

        # 2. Look for an existing review by THIS user for THIS product
        review = db.query(ProductReview).filter(
            ProductReview.productId == product_id,
            ProductReview.userId == user_id
        ).first()

        if review:
            # --- UPDATE LOGIC (PATCH) ---
            if review_data.rating is not None:
                review.rating = review_data.rating
            if review_data.comment is not None:
                review.comment = review_data.comment
            message = "Review updated successfully"
        else:
            # --- CREATE LOGIC (POST) ---
            review = ProductReview(
                productId=product_id,
                userId=user_id,
                rating=review_data.rating,
                comment=review_data.comment
            )
            db.add(review)
            message = "Review submitted successfully"

        # 3. Save changes to the review table
        db.commit()
        db.refresh(review)

        # 4. Recalculate Product Average Rating
        # We do this after the commit so the math includes the new/updated values
        avg_val = db.query(func.avg(ProductReview.rating)).filter(
            ProductReview.productId == product_id
        ).scalar()
        
        if avg_val is not None:
            product.averageRating = round(float(avg_val), 1)
            db.commit()

        return APIHelper.send_success_response(
            data={
                "rating": review.rating,
                "comment": review.comment,
                "product_average": product.averageRating
            }, 
            successMessageKey="translations.SUCCESS" # Or map to a specific key
        )
        