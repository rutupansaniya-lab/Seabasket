# routes/product.py
from fastapi import APIRouter, Depends, Path, Query, status
from typing import Optional
from config.db_config import db_dependency
from controllers.product_controller import ProductController, ProductController2
from dtos.product_model import ProductSort, ProductTrending

product = APIRouter(tags=['products'], prefix='/products')

@product.get("/reviews/{product_id}")
async def get_product_reviews(product_id: int, db: db_dependency):
    return ProductController.get_product_reviews(db, product_id)

@product.get("/get-product/{product_id}")
async def get_product_detail(db: db_dependency, product_id: int = Path(gt=0)):
    return ProductController2.get_product_detail(db, product_id)


@product.get("/all")
async def get_products(
    db: db_dependency,
    product_id:int=None,
    name: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    min_discount: Optional[float] = Query(None),
    sort: Optional[ProductSort] = Query(None),
    is_trending: Optional[ProductTrending]=Query(None)
):
    return ProductController2.get_all_products_unified(
        db,product_id, name, category_id, min_price, max_price, min_rating,min_discount, sort,is_trending
    )

