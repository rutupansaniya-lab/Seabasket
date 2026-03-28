from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from passlib.context import CryptContext
from sqlalchemy import asc, desc, func, or_
from helper.api_helper import APIHelper
from models.sizes_table import ProductSizes
from models.users_table import Users
from config.db_config import db_dependency
from helper.hashing import Hash
from models.cetegories_table import Categories
from models.products_table import Products
from models.users_table import Users
from models.reviews_table import ProductReview
from routes.users import user_dependency
# Declaring router

class ProductController:
    def get_product_reviews(db, product_id):

        product = db.query(Products).filter(Products.id == product_id).first()
        if not product:
            return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")
        
        results = db.query(ProductReview, Users).join(
            Users, ProductReview.userId == Users.id
        ).filter(ProductReview.productId == product_id).all()

        review_list = []
        for review, user in results:
            review_list.append({
                "review_id": review.id,
                "user_name": user.username, # <--- Much better for UI
                "rating": review.rating,
                "comment": review.comment,   # <--- Rich content
                "created_at": review.createdAt.strftime("%Y-%m-%d")
            })

        response_data= {
            "product_id": product_id,
            "product_name": product.name,
            "average_rating": product.averageRating or 0.0,
            "total_reviews": len(review_list),
            "reviews": review_list
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
        )
        
from sqlalchemy import asc, desc, func
from fastapi import HTTPException
from models.products_table import Products
from models.cetegories_table import Categories

from fastapi import HTTPException
from sqlalchemy import or_, asc, desc

class ProductController2:
    @staticmethod
    def get_all_products_unified(
        db,
        product_id=None,   
        name=None,
        category_id=None,
        min_price=None,
        max_price=None,
        min_rating=None,
        min_discount=None,
        sort=None,
        is_trending=None
    ):

        # ✅ 1. If product_id is provided → return single product detail
        if product_id is not None:

            if product_id <= 0:
                return APIHelper.send_error_response(errorMessageKey="translations.INVAID_ID")
        

            product = db.query(Products).filter(Products.id == product_id).first()

            if not product:
                return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")

            # ✅ Build available sizes
            size_mapping = {
                "S": product.small_size_stock,
                "M": product.medium_size_stock,
                "L": product.large_size_stock,
                "XL": product.extra_large_size_stock
            }

            available_sizes = [size for size, stock in size_mapping.items() if stock > 0]

            response_data= {
                "product": product,
                "available_sizes": available_sizes
            }

            return APIHelper.send_success_response(
                data=response_data, 
                successMessageKey="translations.SUCCESS"
            )

        # ✅ 2. Otherwise → normal listing logic
        query = db.query(Products)

        # Search + Category
        if name or category_id:
            query = query.join(Categories, Products.categoryId == Categories.id)

            if name:
                query = query.filter(
                    or_(
                        Products.name.ilike(f"%{name}%"),
                        Products.description.ilike(f"%{name}%")
                    )
                )

            if category_id:
                category = db.query(Categories).filter(Categories.id == category_id).first()
                if not category:
                    return APIHelper.send_not_found_error(errorMessageKey="translations.CATEGORY_NOT_FOUND")

                query = query.filter(Products.categoryId == category_id)

        # Price + Rating
        if min_price is not None:
            query = query.filter(Products.price >= min_price)

        if max_price is not None:
            query = query.filter(Products.price <= max_price)

        if min_rating is not None:
            query = query.filter(Products.averageRating >= min_rating)

        if min_discount is not None:
            query = query.filter(Products.discountPercentage >= min_discount)

        # Sorting
        if sort == "price_low":
            query = query.order_by(asc(Products.price))
        elif sort == "price_high":
            query = query.order_by(desc(Products.price))
        elif sort == "name_asc":
            query = query.order_by(asc(Products.name))

        # Trending
        if is_trending is not None:
            query = query.filter(Products.isTrending == True)

        products = query.all()

        return products

    def get_product_detail(db, product_id: int):
        if product_id <= 0:
            return APIHelper.send_error_response(errorMessageKey="translations.INVAID_ID")

        product = db.query(Products).filter(Products.id == product_id).first()

        if not product:
            return APIHelper.send_not_found_error(errorMessageKey="translations.PRODUCT_NOT_FOUND")

        # ✅ Build available sizes from product table
        available_sizes = []

        if product.small_size_stock > 0:
            available_sizes.append("S")

        if product.medium_size_stock > 0:
            available_sizes.append("M")

        if product.large_size_stock > 0:
            available_sizes.append("L")

        if product.extra_large_size_stock > 0:
            available_sizes.append("XL")

        original_price = float(product.price) if product.price else 0.0
        discount_percent = float(product.discountPercentage) if product.discountPercentage else 0.0
        

        discount_amount = (original_price * discount_percent) / 100
        discounted_price = round(original_price - discount_amount, 2)

        product_data = {
                "id": product.id,
                "name": product.name,
                "price":float(product.price),
                "discountedPrice": discounted_price,
                "description": product.description,
                "categoryId": product.categoryId,
                "imageUrl": product.imageUrl,
                "averageRating": product.averageRating,
                "discountPercentage": product.discountPercentage,
                "isTrending": product.isTrending
            }

        response_data = {
            "product": product_data,
            "available_sizes": available_sizes
        }

        return APIHelper.send_success_response(
            data=response_data, 
            successMessageKey="translations.SUCCESS"
        )
            