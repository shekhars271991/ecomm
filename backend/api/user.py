import time
from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash


def create_user_resource(db, models, db_tracker, create_api_response):
    """Factory function to create UserResource with initialized dependencies"""
    
    User = models['User']
    
    class UserResource(Resource):
        def post(self):
            data = request.get_json()
            
            if not data or 'email' not in data:
                return create_api_response(None, False, "Email is required"), 400
            
            # Check if this is login or registration
            if 'password' not in data:
                return create_api_response(None, False, "Password is required"), 400
            
            start_time = time.time()
            existing_user = User.query.filter_by(email=data['email']).first()
            end_time = time.time()
            
            db_tracker.log_query('SELECT', f"SELECT * FROM users WHERE email = '{data['email']}'", start_time, end_time, 1 if existing_user else 0, database_type='mysql')
            
            if existing_user:
                # Login attempt
                if check_password_hash(existing_user.password_hash, data['password']):
                    user_data = {
                        'id': existing_user.id,
                        'email': existing_user.email,
                        'name': existing_user.name,
                        'address': existing_user.address,
                        'phone': existing_user.phone
                    }
                    return create_api_response({'user': user_data}, True, "Login successful")
                else:
                    return create_api_response(None, False, "Invalid credentials"), 401
            else:
                # Registration
                if 'name' not in data:
                    return create_api_response(None, False, "Name is required for registration"), 400
                
                new_user = User(
                    email=data['email'],
                    password_hash=generate_password_hash(data['password']),
                    name=data['name'],
                    address=data.get('address', ''),
                    phone=data.get('phone', '')
                )
                
                start_time = time.time()
                db.session.add(new_user)
                db.session.commit()
                end_time = time.time()
                
                db_tracker.log_query('INSERT', f"INSERT INTO users (email, name, ...) VALUES ('{data['email']}', '{data['name']}', ...)", start_time, end_time, 1, database_type='mysql')
                
                user_data = {
                    'id': new_user.id,
                    'email': new_user.email,
                    'name': new_user.name,
                    'address': new_user.address,
                    'phone': new_user.phone
                }
                
                return create_api_response({'user': user_data}, True, "Registration successful"), 201
    
    return UserResource 