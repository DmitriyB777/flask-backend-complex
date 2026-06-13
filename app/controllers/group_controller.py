from flask import Blueprint, jsonify
from ..models.group import Group

group_controller = Blueprint('group', __name__)

@group_controller.get('/groups')
def get_groups():
    groups = Group.query.all()
    return jsonify({'name': 'hello get'})

@group_controller.post('/group')
def add_group():
    return jsonify({'name': 'hello post'})

@group_controller.put('/group')
def update_group():
    return jsonify({'name': 'hello put'})

@group_controller.delete('/group')
def delete_group():
    return jsonify({'name': 'hello delete'})