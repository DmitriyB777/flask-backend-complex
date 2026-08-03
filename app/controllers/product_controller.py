from flask import Blueprint, jsonify, request
from ..models.group import Group
from ..models.product import Product
from ..extensions import db

product_controller = Blueprint('product', __name__)

@product_controller.get('/products')
@product_controller.get('/products/<int:group_id>')
def get_products(group_id=None):
    if group_id is None:
        all_products = Product.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'group_id': p.group_id} for p in all_products])

    group = Group.query.get(group_id)

    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    products = Product.query.filter(Product.group_id == group_id).all()
    sub_groups = Group.query.filter(Group.parent_id == group_id).all()

    data = {
        'products': products,
        'sub_groups': sub_groups
    }

    if data:
        return jsonify(data)
    else:
        return jsonify({'message': 'No products or sub-groups found for this region'}), 404

@product_controller.post('/product')
def add_product():
    try:
        data = request.get_json()

        # need to add checking right of user

        if not data or 'name' not in data or 'group_id' not in data:
            return jsonify({"error": "Bad Request"}), 400
        
        if data['group_id'] is None:
            return jsonify({"error": "Bad Request"}), 400

        product = Product(name = data['name'], group_id = data['group_id'])

        db.session.add(product)

        db.session.commit()

        return jsonify({'id': product.id, 'name': product.name, 'group_id': product.group_id}), 201
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@product_controller.put('/product/<int:id>')
def update_product(id):
    try:
        product = db.session.get(Product, id)

        if not product:
            return jsonify({"error": "Not found"}), 404

        # need to add checking right of user

        data = request.get_json()

        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        if 'name' in data:
            product.name = data['name']
        
        if 'group_id' in data:
            product.group_id = data['group_id']
        
        db.session.commit()

        return jsonify({'id': product.id, 'name': product.name, 'group_id': product.group_id}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@product_controller.delete('/product/<int:id>')
def delete_product(id):
    try:
        product = db.session.get(Product, id)

        # need to add checking right of user

        if not product:
            return jsonify({"error": "Not found"}), 404
        
        db.session.delete(product)

        db.session.commit()

        return jsonify({'message': 'The item was successfully deleted'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500