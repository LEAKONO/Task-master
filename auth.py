from flask import Blueprint, request, jsonify
from app import db
from models import User, TokenBlocklist
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from schemas import UserSchema
from marshmallow import ValidationError

bp = Blueprint('auth', __name__, url_prefix='/auth')
user_schema = UserSchema()

import logging
# Configure logging at the beginning of your file
logging.basicConfig(level=logging.INFO)

@bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        logging.info("Received signup data: %s", data)
        
        # Validate and load user data
        user_data = user_schema.load(data)

        # Check for existing user
        if User.query.filter_by(email=user_data['email']).first():
            return jsonify({"error": "Email already exists"}), 400

        # Create a new user
        user = User(username=user_data['username'], email=user_data['email'])
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.commit()

        logging.info("User created successfully")
        return jsonify({"message": "User created successfully"}), 201

    except ValidationError as err:
        logging.error("Validation error: %s", err.messages)
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        logging.error("Unhandled exception in signup: %s", str(e))
        return jsonify({"message": "Signup failed", "error": str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blocklist_entry = TokenBlocklist(jti=jti)
    db.session.add(blocklist_entry)
    db.session.commit()

    return jsonify({"msg": "Successfully logged out"}), 200
