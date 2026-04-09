from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app.services.category_service import CategoryService

category_blueprint = Blueprint('category', __name__)

@category_blueprint.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('type'):
        return jsonify({"error": "Missing name or type in request body"}), 400

    try:
        new_category = CategoryService.create_category(
            user=current_user,
            category_name=data['name'],
            category_type=data['type']
        )
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@category_blueprint.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    try:
        CategoryService.delete_category(
            user=current_user,
            category_id=category_id
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@category_blueprint.route('/api/categories', methods=['GET'])
@login_required
def list_categories():
    categories = CategoryService.get_all_categories(current_user)
    return jsonify(categories), 200
