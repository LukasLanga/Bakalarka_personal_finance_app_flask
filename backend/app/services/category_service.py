from sqlalchemy import or_
from backend.app.db import db
from backend.app.models import Category
from backend.app.models.user import User
from backend.app.models import Transaction

class CategoryService:

    @staticmethod
    def get_all_categories(user: User):
        return Category.query.filter(or_(Category.user_id == user.id, Category.user_id == 0)).all()

    @staticmethod
    def create_category(user: User, category_name, category_type):
        current_categories = CategoryService.get_all_categories(user)
        if any(cat.name.lower() == category_name.lower() for cat in current_categories):
            raise ValueError('Category with this name already exists')
        
        category = Category(user_id=user.id, name=category_name, type=category_type)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def delete_category(user: User, category_id):
        category = Category.query.get(category_id)

        if not category:
            raise ValueError('Category not found')

        if category.user_id == 0:
            raise PermissionError('Cannot remove a default category.')
        if category.user_id != user.id:
            raise PermissionError('You do not have permission to delete this category.')

        # What to do with a category that has items?
        # My recommendation: Do not allow it. This check prevents orphaned data.
        if Transaction.query.filter_by(category_id=category.id).first():
            raise ValueError(f"Cannot delete category '{category.name}' as it is currently in use.")

        db.session.delete(category)
        db.session.commit()
        return True

    @staticmethod
    def user_category_exists(user: User, category_id):
        category = Category.query.get(category_id)
        if not category:
            return False
        return category.user_id == user.id or category.user_id == 0
