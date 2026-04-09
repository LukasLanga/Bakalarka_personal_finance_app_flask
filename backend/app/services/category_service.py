from sqlalchemy import or_, func
from backend.app.db import db
from backend.app.models import Category
from backend.app.models.user import User
from backend.app.models import Transaction

class CategoryService:

    @staticmethod
    def get_all_categories(user: User):
        usage_subquery = db.session.query(
            Transaction.category_id,
            func.count(Transaction.id).label('usage_count')
        ).group_by(Transaction.category_id).subquery()

        categories_with_counts = db.session.query(
            Category,
            usage_subquery.c.usage_count
        ).outerjoin(
            usage_subquery, Category.id == usage_subquery.c.category_id
        ).filter(
            or_(Category.user_id == user.id, Category.user_id == 0)
        ).all()

        result = []
        for category, count in categories_with_counts:
            cat_dict = category.to_dict(usage_count=count or 0)
            result.append(cat_dict)
            
        return result

    @staticmethod
    def create_category(user: User, category_name, category_type):
        current_categories_data = CategoryService.get_all_categories(user)
        if any(cat['name'].lower() == category_name.lower() for cat in current_categories_data):
            raise ValueError('Category with this name already exists')
        
        category = Category(user_id=user.id, name=category_name, type=category_type)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def delete_category(user: User, category_id: int):
        category = Category.query.filter_by(user_id=user.id, id=category_id).first()

        if not category:
            raise ValueError('Category not found')

        if category.user_id == 0:
            raise PermissionError('Cannot remove a default category.')

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
