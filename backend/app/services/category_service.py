from sqlalchemy import or_
from backend.app.db import db
from backend.app.models import Category
from backend.app.models.user import User

class CategoryService:

    @staticmethod
    def get_all_categories(user: User):
        return Category.query.filter(or_(Category.user_id == user.id, Category.user_id == 0)).all()


    @staticmethod
    def create_category(user: User, category_name, category_type):
        current_categories = CategoryService.get_all_categories(user)
        if any(cat.name.lower() == category_name.lower() for cat in current_categories):
            raise Exception('Category already exists')
        category = Category(user_id = user.id,name=category_name, category_type=category_type)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def delete_category(user: User, category_id):
        category = Category.query.get(category_id)

        if not category:
            raise Exception('Category not found')

        if category.user_id == 0:
            raise Exception('Cant remove default category')

        if category.user_id != user.id:
            raise Exception('Category not found')

        db.session.delete(category)
        db.session.commit()
        return True

    @staticmethod
    def user_category_exists(user: User, category_id):
        category = Category.query.get(category_id)
        if not category:
            return False
        if category.user_id != user.id:
            return False
        return True

