from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import select, delete
from ..models.group import Group
from ..models.product import Product
from ..models.user import User
from ..models.rights_user import RightsUser
from ..extensions import db
from flask_jwt_extended import get_jwt_identity

group_controller = Blueprint('group', __name__)

@group_controller.get('/groups')
@jwt_required()
def get_groups():
    try:
        identity = get_jwt_identity()

        query = select(User).filter_by(username=identity)
        user = db.session.execute(query).scalar_one_or_none()

        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        query = select(Group).join(RightsUser).filter(RightsUser.user_id == user.id)
        groups = db.session.execute(query).scalars().all()

        return jsonify([{'id': g.id, 'name': g.name, 'parent_id': g.parent_id} for g in groups])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@group_controller.post('/group')
@jwt_required()
def add_group():
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'parent_id' not in data:
            return jsonify({"error": "Bad Request"}), 400
        
        parent = db.session.get(Group, data['parent_id'])
        
        # Parent group not found
        if not parent and data['parent_id'] is not None:
            return jsonify({"error": "Not found"}), 404

        identity = get_jwt_identity()
        
        query = select(User).filter_by(username=identity)
                
        user = db.session.execute(query).scalar_one_or_none()
        
        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        group = Group(name = data['name'], parent_id = data['parent_id'])

        db.session.add(group)

        db.session.flush()

        rights = RightsUser(user_id = user.id, group_id = group.id)

        db.session.add(rights)
        
        db.session.commit()

        return jsonify({'id': group.id, 'name': group.name, 'parent_id': group.parent_id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@group_controller.put('/group/<int:id>')
@jwt_required()
def update_group(id):
    try:
        group = db.session.get(Group, id)

        if not group:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json()

        if not data:
            return jsonify({"error": "Bad Request"}), 400

        identity = get_jwt_identity()

        query = select(User).filter_by(username=identity)
                       
        user = db.session.execute(query).scalar_one_or_none()

        if not user:
            return jsonify({"error": "Unauthorized"}), 401

        query = select(RightsUser).filter_by(user_id=user.id, group_id=id)

        rights = db.session.execute(query).scalar_one_or_none()

        if not rights:
            return jsonify({"error": "Forbidden"}), 403
        
        if 'name' in data:
            group.name = data['name']
        
        if 'parent_id' in data:

            # A group cannot be its own parent
            if data['parent_id'] == id:
                return jsonify({"error": "Bad Request"}), 400

            parent = db.session.get(Group, data['parent_id'])

            # Parent group not found
            if not parent and data['parent_id'] is not None:
                return jsonify({"error": "Not found"}), 404

            descendants = get_all_descendant_groups(id) 

            # Cannot move a group to one of its own descendants
            if data['parent_id'] in descendants:
                return jsonify({"error": "Bad Request"}), 400
            
            group.parent_id = data['parent_id']
        
        db.session.commit()

        return jsonify({'id': group.id, 'name': group.name, 'parent_id': group.parent_id}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@group_controller.delete('/group/<int:id>')
@jwt_required()
def delete_group(id):
    try:
        group = db.session.get(Group, id)

        if not group:
            return jsonify({"error": "Not found"}), 404

        identity = get_jwt_identity()

        query = select(User).filter_by(username=identity)           
        user = db.session.execute(query).scalar_one_or_none()

        if not user:
            return jsonify({"error": "Unauthorized"}), 401
                        
        query = select(RightsUser).filter(RightsUser.user_id == user.id, RightsUser.group_id == id)
        rights = db.session.execute(query).scalar_one_or_none()
                
        if not rights:
            return jsonify({"error": "Forbidden"}), 403

        groups_ids_to_remove = get_all_descendant_groups(group.id)

        subquery = select(RightsUser.id).where(
            RightsUser.user_id == user.id, 
            RightsUser.group_id == Group.id
        )

        query = select(Group.id).where(
            Group.id.in_(groups_ids_to_remove),
            ~subquery.exists()
        )
        
        unauthorized_groups = db.session.execute(query).scalars().all()

        if unauthorized_groups:
            return jsonify({"error": "Forbidden"}), 403

        query = delete(Product).where(Product.group_id.in_(groups_ids_to_remove))
        db.session.execute(query)

        query = delete(RightsUser).where(RightsUser.group_id.in_(groups_ids_to_remove))
        db.session.execute(query)

        query = delete(Group).where(Group.id.in_(groups_ids_to_remove))
        db.session.execute(query)

        db.session.commit()

        return jsonify({'message': 'The item was successfully deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def get_all_descendant_groups(group_id):
    descendant_groups_ids = set()
    groups_to_process = [group_id]

    while groups_to_process:
        current_group_id = groups_to_process.pop()
        descendant_groups_ids.add(current_group_id)

        query = select(Group).filter_by(parent_id=current_group_id)
        subgroups = db.session.execute(query).scalars().all()

        for subgroup in subgroups:
            groups_to_process.append(subgroup.id)
            
    return list(descendant_groups_ids)