from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from ..models.group import Group
from ..models.product import Product
from ..models.user import User
from ..models.rights_user import RightsUser
from ..extensions import db
from flask_jwt_extended import get_jwt_identity

product_controller = Blueprint('product', __name__)

@product_controller.get('/products')
@product_controller.get('/products/<int:group_id>')
@jwt_required()
def get_products(group_id=None):
    try:
        identity = get_jwt_identity()
                
        query = select(User).filter_by(username=identity)
                        
        user = db.session.execute(query).scalar_one_or_none()
                
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        if group_id is None:
            query = select(Product).join(RightsUser).filter(RightsUser.user_id == user.id)
            all_products = db.session.execute(query).scalars().all()

            return jsonify([{'id': p.id, 'name': p.name, 'group_id': p.group_id} for p in all_products])

        query = select(Group).filter_by(group_id=group_id)
        group = db.session.execute(query).scalar_one_or_none()

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        query = select(Group).join(RightsUser).filter(RightsUser.user_id == user.id, RightsUser.group_id == group_id)
        group = db.session.execute(query).scalar_one_or_none()

        if not group:
            return jsonify({"error": "Forbidden"}), 403

        # query = select(Product).filter_by(group_id=group_id)
        query = select(Product).join(RightsUser).filter(RightsUser.user_id == user.id, RightsUser.group_id == group_id)
        products = db.session.execute(query).scalars().all()

        # query = select(Group).filter_by(parent_id=group_id)
        query = select(Group).join(RightsUser).filter(RightsUser.user_id == user.id, Group.parent_id == group_id)
        sub_groups = db.session.execute(query).scalars().all()

        data = {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'group_id': p.group_id
                } for p in products
            ],
            'sub_groups': [
                {
                    'id': g.id,
                    'name': g.name,
                    'parent_id': g.parent_id
                } for g in sub_groups
            ]
        }

        if products or sub_groups:
            return jsonify(data)
        else:
            return jsonify({'message': 'No products or sub-groups found for this region'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@product_controller.post('/product')
@jwt_required()
def add_product():
    try:
        data = request.get_json()

        identity = get_jwt_identity()
                        
        query = select(User).filter_by(username=identity)

        user = db.session.execute(query).scalar_one_or_none()
                        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        if not data or 'name' not in data or 'group_id' not in data:
            return jsonify({"error": "Bad Request"}), 400
        
        if data['group_id'] is None:
            return jsonify({"error": "Bad Request"}), 400

        parent = db.session.get(Group, data['group_id'])

        if not parent:
            return jsonify({"error": "Group not found"}), 404

        query = select(RightsUser).filter_by(user_id=user.id, group_id=data['group_id'])

        rights = db.session.execute(query).scalar_one_or_none()
        
        if not rights:
            return jsonify({"error": "Forbidden"}), 403

        product = Product(name = data['name'], group_id = data['group_id'])

        db.session.add(product)

        db.session.commit()

        return jsonify({'id': product.id, 'name': product.name, 'group_id': product.group_id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@product_controller.put('/product/<int:id>')
@jwt_required()
def update_product(id):
    try:
        product = db.session.get(Product, id)

        if not product:
            return jsonify({"error": "Not found"}), 404

        identity = get_jwt_identity()
                                
        query = select(User).filter_by(username=identity)
        
        user = db.session.execute(query).scalar_one_or_none()
                                
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()

        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        if 'group_id' in data and 'name' in data:
            if data['group_id'] is None:
                return jsonify({"error": "Bad Request"}), 400

            parent = db.session.get(Group, data['group_id'])
            
            if not parent:
                return jsonify({"error": "Group not found"}), 404

            query = select(RightsUser).filter_by(user_id=user.id, group_id=data['group_id'])
            
            rights = db.session.execute(query).scalar_one_or_none()
                    
            if not rights:
                return jsonify({"error": "Forbidden"}), 403

            product.name = data['name']
            product.group_id = data['group_id']
        
        db.session.commit()

        return jsonify({'id': product.id, 'name': product.name, 'group_id': product.group_id}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@product_controller.delete('/product/<int:id>')
@jwt_required()
def delete_product(id):
    try:
        product = db.session.get(Product, id)

        identity = get_jwt_identity()
                                        
        query = select(User).filter_by(username=identity)
                
        user = db.session.execute(query).scalar_one_or_none()
                                        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        if not product:
            return jsonify({"error": "Not found"}), 404

        query = select(RightsUser).filter_by(user_id=user.id, group_id=product.group_id)
                    
        rights = db.session.execute(query).scalar_one_or_none()
                            
        if not rights:
            return jsonify({"error": "Forbidden"}), 403
        
        db.session.delete(product)

        db.session.commit()

        return jsonify({'message': 'The item was successfully deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500