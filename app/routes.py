from flask import Blueprint, request, jsonify
from . import db
from .models import User
from .utils import hash_password, check_password
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import json 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not ('email' in data and 'password' in data and 'username' in data):
        return jsonify({"message": "Registration data missing.  Make sure you include username, password and email"}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password=hash_password(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password(user.password, data['password']):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token(identity=user.username)
    return jsonify({"access_token": token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    else:
        return jsonify({
            'message': 'User does not exist in the database'
        }), 403
    
