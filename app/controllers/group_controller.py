from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ..models.group import Group
from ..models.product import Product
from ..extensions import db

group_controller = Blueprint('group', __name__)

@group_controller.get('/groups')
# @jwt_required()
def get_groups():
    # need to add checking right of user

    groups = Group.query.all()

    return jsonify([{'id': g.id, 'name': g.name, 'parent_id': g.parent_id} for g in groups])

@group_controller.post('/group')
# @jwt_required()
def add_group():
    try:
        data = request.get_json()

        # need to add checking right of user

        if not data or 'name' not in data or 'parent_id' not in data:
            return jsonify({"error": "Bad Request"}), 400

        group = Group(name = data['name'], parent_id = data['parent_id'])

        db.session.add(group)

        db.session.commit()

        return jsonify({'id': group.id, 'name': group.name, 'parent_id': group.parent_id}), 201
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@group_controller.put('/group/<int:id>')
# @jwt_required()
def update_group(id):
    try:
        group = db.session.get(Group, id)

        if not group:
            return jsonify({"error": "Not found"}), 404

        # need to add checking right of user

        data = request.get_json()

        if not data:
            return jsonify({"error": "Bad Request"}), 400
        
        if 'name' in data:
            group.name = data['name']
        
        if 'parent_id' in data:
            group.parent_id = data['parent_id']
        
        db.session.commit()

        return jsonify({'id': group.id, 'name': group.name, 'parent_id': group.parent_id}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

@group_controller.delete('/group/<int:id>')
# @jwt_required()
def delete_group(id):
    try:
        group = db.session.get(Group, id)

        if not group:
            return jsonify({"error": "Not found"}), 404

        # need to add checking right of user

        groups_ids_to_remove = get_all_descendant_groups(group.id)

        products_to_remove = Product.query.filter(Product.group_id.in_(groups_ids_to_remove)).all()

        for p in products_to_remove:
            db.session.delete(p)
        
        groups_to_remove_objects = Group.query.filter(Group.id.in_(groups_ids_to_remove)).all()
        for g in groups_to_remove_objects:
            db.session.delete(g)

        db.session.commit()

        return jsonify({'message': 'The item was successfully deleted'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 500

def get_all_descendant_groups(group_id):
    descendant_groups_ids = set()
    groups_to_process = [group_id]

    while groups_to_process:
        current_group_id = groups_to_process.pop()
        descendant_groups_ids.add(current_group_id)

        subgroups = Group.query.filter_by(parent_id=current_group_id).all()
        for subgroup in subgroups:
            groups_to_process.append(subgroup.id)
            
    return list(descendant_groups_ids)