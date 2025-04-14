from datetime import timedelta
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)

from app.services.facade import HBnBFacade
from app.models.user import User

api = Namespace('auth', description='User authentication')

facade = HBnBFacade()

# ===== Models =====
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = api.model('Register', {
    'first_name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# ===== Routes =====

@api.route('/login')
class LoginResource(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        user = facade.get_user_by_email(credentials['email'])

        if not user or not user.check_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin},
            expires_delta=timedelta(days=1)
        )
        return {'access_token': access_token}, 200


@api.route('/register')
class RegisterResource(Resource):
    @api.expect(register_model)
    def post(self):
        """Register a new user"""
        data = api.payload
        existing_user = facade.get_user_by_email(data['email'])

        if existing_user:
            return {'error': 'Email already exists!'}, 400

        try:
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                password=data['password']
            )
            facade.save_user(new_user)
        except ValueError as e:
            return {'error': str(e)}, 400

        access_token = create_access_token(
            identity=str(new_user.id),
            additional_claims={"is_admin": new_user.is_admin},
            expires_delta=timedelta(days=1)
        )
        return {'access_token': access_token}, 201


@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        """Example protected endpoint"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        return {
            'message': f'Hello, user {current_user_id}',
            'is_admin': claims.get("is_admin", False)
        }, 200


@api.route('/generate_admin_token')
class GenerateAdminToken(Resource):
    def get(self):
        """Temporary utility to generate a static admin token (for testing)"""
        token = create_access_token(
            identity="admin",
            expires_delta=timedelta(days=365),
            additional_claims={"is_admin": True}
        )
        return {'admin_token': token}
