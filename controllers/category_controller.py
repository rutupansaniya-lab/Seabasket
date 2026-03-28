# controllers/category_controller.py
from helper.api_helper import APIHelper
from models.cetegories_table import Categories

class CategoryController:
    def get_all_categories(db):
    
        categories_raw = db.query(Categories).all()

        category_list = []
        for cat in categories_raw:
            # Manually building the dictionary ensures Pydantic can serialize it
            category_list.append({
                "id": cat.id,
                "name": cat.name,
                "createdAt": cat.createdAt.strftime("%Y-%m-%d %H:%M:%S") if cat.createdAt else None,
                "updatedAt": cat.updatedAt.strftime("%Y-%m-%d %H:%M:%S") if cat.updatedAt else None
            })

        return APIHelper.send_success_response(
            data=category_list, 
            successMessageKey="translations.SUCCESS"
        )