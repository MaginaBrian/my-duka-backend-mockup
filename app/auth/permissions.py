# app/auth/permissions.py

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user_models import Merchant # Import Merchant from the new user_models file

def merchant_required():
    """
    Decorator to ensure the current authenticated user is a Merchant (superuser).
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity() # Get the user ID from the JWT
            merchant = Merchant.query.get(current_user_id)

            if not merchant or not merchant.is_superuser:
                return jsonify({'message': 'Merchant (Superuser) access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Add more permission decorators here as needed (e.g., admin_required, clerk_required)
