# routes/user.py
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated, Optional
from pydantic import EmailStr
from config.db_config import db_dependency
from helper.token_helper import TokenHelper
from controllers.user_controller import UserController
from dtos.auth_models import UserModel
from dtos.user_models import ChangePasswordModel, ForgotPasswordModel, ResetPasswordModel, UpdateEmailRequestModel, UpdatePhoneNumberRequestModel, UpdateUserRequest
from dtos.product_model import ProductReview
user = APIRouter(tags=['User'], prefix='/user')

# Define the user dependency once for reuse
user_dependency = Annotated[dict, Depends(TokenHelper.get_current_user)]

@user.post('/register', status_code=201)
async def register(db: db_dependency, user_data: UserModel):
    return UserController.create_user(db, user_data)

@user.patch("/change-password")
async def change_password(db: db_dependency, password_data: ChangePasswordModel, current_user: user_dependency):
    return UserController.change_password(db, password_data, current_user)

@user.post("/forgot-password")
async def forgot_password(password_data: ForgotPasswordModel,db: db_dependency):
    return UserController.forgot_password(password_data, db)

@user.patch("/reset-password")
async def reset_password(password_data: ResetPasswordModel,current_user: user_dependency,db:db_dependency):
    return UserController.reset_password(password_data,current_user,db)

@user.post("/product/review")
async def review(db: db_dependency, review_data: ProductReview, current_user: user_dependency):
    return UserController.add_review(db, review_data, current_user)

@user.patch("/product/{product_id}/my-review")
def manage_my_review(
    product_id: int,
    db: db_dependency,
    user: user_dependency,
    rating: Optional[float] = Query(None,ge=1, le=5),
    comment: Optional[str] = Query(None)
):
    return UserController.manage_review_patch(
        db=db, 
        current_user=user, 
        product_id=product_id, 
        rating=rating, 
        comment=comment
    )

@user.put("/profile")
async def update_user(
    current_user: user_dependency,
    request: UpdateUserRequest,
    db: db_dependency
):
    return UserController.update_user_service(current_user, request, db)

@user.post("/product/add/update/review")
async def submit_or_update_review(
    db: db_dependency, 
    review_data: ProductReview, 
    current_user: user_dependency
):
    return UserController.manage_review(db, review_data, current_user)

