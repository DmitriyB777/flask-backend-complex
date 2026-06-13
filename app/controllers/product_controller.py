from flask import Blueprint, jsonify
from ..models.product import Product

product_controller = Blueprint('product', __name__)

@product_controller.get('/products')
def get_products():
    products = Product.query.all()
    return jsonify({'name': 'hello get'})

@product_controller.post('/product')
def add_product():
    return jsonify({'name': 'hello post'})

@product_controller.put('/product')
def update_product():
    return jsonify({'name': 'hello put'})

@product_controller.delete('/product')
def delete_product():
    return jsonify({'name': 'hello delete'})