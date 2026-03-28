# routes/category.py
from fastapi import APIRouter
from config.db_config import db_dependency
from controllers.category_controller import CategoryController

category = APIRouter(tags=['category'], prefix='/category')

@category.get("/all-categories")
async def get_all_categories(db: db_dependency):
    return CategoryController.get_all_categories(db)