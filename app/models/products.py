# app/models/product.py

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # Import get_jwt
from sqlalchemy.exc import IntegrityError

from app import db # Import db from your app initialization
from app.models.user_models import Merchant, Admin, Clerk # Import user models
from app.auth.permissions import merchant_required, admin_required, clerk_required # Import permission decorators
from datetime import datetime

# Create a Blueprint for product-related routes
product_bp = Blueprint('product_bp', __name__)
api = Api(product_bp)

class Product(db.Model):
    """
    Represents a product item available in the inventory system.
    """
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False) # Products can be active/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'buying_price': self.buying_price,
            'selling_price': self.selling_price,
            'merchant_id': self.merchant_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# --- API Resources ---

class ProductListResource(Resource):
    """
    Handles listing all products and creating new products.
    Merchant and Admin can create products. All roles can view products.
    """
    @jwt_required()
    def get(self):
        # Get user type from JWT claims
        claims = get_jwt()
        user_type = claims.get('user_type')

        # All authenticated users (merchant, admin, clerk) can view products
        if user_type not in ['merchant', 'admin', 'clerk']:
            return {'message': 'Authentication required to view products'}, 403

        # For now, all products are visible to all users.
        # In a multi-merchant setup, you'd filter by merchant_id.
        products = Product.query.all()
        return {'products': [product.to_dict() for product in products]}, 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_type = claims.get('user_type')

        # Only Merchant or Admin can create products
        if user_type not in ['merchant', 'admin']:
            return {'message': 'Merchant or Admin access required to create products'}, 403

        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        buying_price = data.get('buying_price')
        selling_price = data.get('selling_price')

        if not all([name, buying_price, selling_price is not None]): # selling_price can be 0.0
            return {'message': 'Missing required fields: name, buying_price, selling_price'}, 400

        try:
            buying_price = float(buying_price)
            selling_price = float(selling_price)
            if buying_price < 0 or selling_price < 0:
                return {'message': 'Prices cannot be negative'}, 400
        except ValueError:
            return {'message': 'Buying and selling prices must be valid numbers'}, 400

        # Determine the merchant_id for the product based on the user type
        if user_type == 'merchant':
            product_merchant_id = current_user_id
        elif user_type == 'admin':
            admin = Admin.query.get(current_user_id)
            if not admin:
                return {'message': 'Admin not found for product creation'}, 404
            product_merchant_id = admin.merchant_id
        else:
            # This case should ideally be caught by the initial permission check,
            # but as a fallback, it's good to have.
            return {'message': 'Unauthorized to create products'}, 403


        try:
            new_product = Product(
                name=name,
                description=description,
                buying_price=buying_price,
                selling_price=selling_price,
                merchant_id=product_merchant_id
            )
            db.session.add(new_product)
            db.session.commit()
            return {'message': 'Product created successfully', 'product': new_product.to_dict()}, 201
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Product with this name already exists'}, 409
        except Exception as e:
            db.session.rollback()
            print(f"Error creating product: {e}")
            return {'message': 'An internal server error occurred during product creation.'}, 500

class ProductResource(Resource):
    """
    Handles operations on a single product (get, update, delete).
    Merchant and Admin can update. Merchant can delete. All can view.
    """
    @jwt_required()
    def get(self, product_id):
        claims = get_jwt()
        user_type = claims.get('user_type')

        if user_type not in ['merchant', 'admin', 'clerk']:
            return {'message': 'Authentication required to view product'}, 403

        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404

        # For now, any authenticated user can view any product.
        # In a multi-merchant setup, you'd check if product.merchant_id matches user's merchant_id.
        return {'product': product.to_dict()}, 200

    @jwt_required()
    def put(self, product_id):
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_type = claims.get('user_type')

        # Only Merchant or Admin can update products
        if user_type not in ['merchant', 'admin']:
            return {'message': 'Merchant or Admin access required to update products'}, 403

        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404

        # Ensure the product belongs to the current user's merchant
        if user_type == 'merchant':
            if product.merchant_id != current_user_id:
                return {'message': 'Unauthorized to update this product'}, 403
        elif user_type == 'admin':
            admin = Admin.query.get(current_user_id)
            if not admin or product.merchant_id != admin.merchant_id:
                return {'message': 'Unauthorized to update this product'}, 403


        data = request.get_json()
        name = data.get('name', product.name)
        description = data.get('description', product.description)
        buying_price = data.get('buying_price', product.buying_price)
        selling_price = data.get('selling_price', product.selling_price)
        is_active = data.get('is_active', product.is_active)

        if name:
            product.name = name
        if description is not None: # Allow setting description to null
            product.description = description

        # Validate prices if provided
        if buying_price is not None:
            try:
                buying_price = float(buying_price)
                if buying_price < 0:
                    return {'message': 'Buying price cannot be negative'}, 400
                product.buying_price = buying_price
            except ValueError:
                return {'message': 'Buying price must be a valid number'}, 400

        if selling_price is not None:
            try:
                selling_price = float(selling_price)
                if selling_price < 0:
                    return {'message': 'Selling price cannot be negative'}, 400
                product.selling_price = selling_price
            except ValueError:
                return {'message': 'Selling price must be a valid number'}, 400

        if isinstance(is_active, bool):
            product.is_active = is_active

        try:
            db.session.commit()
            return {'message': 'Product updated successfully', 'product': product.to_dict()}, 200
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Product with this name already exists'}, 409
        except Exception as e:
            db.session.rollback()
            print(f"Error updating product: {e}")
            return {'message': 'An internal server error occurred during product update.'}, 500

    @jwt_required()
    @merchant_required() # Only Merchant can delete a product
    def delete(self, product_id):
        current_user_id = get_jwt_identity()
        product = Product.query.get(product_id)
        if not product:
            return {'message': 'Product not found'}, 404

        # Ensure the product belongs to the current merchant
        if product.merchant_id != current_user_id:
            return {'message': 'Unauthorized to delete this product'}, 403

        try:
            db.session.delete(product)
            db.session.commit()
            return {'message': 'Product deleted successfully'}, 204
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting product: {e}")
            return {'message': 'An internal server error occurred during product deletion.'}, 500

# Add resources to the API
api.add_resource(ProductListResource, '/')
api.add_resource(ProductResource, '/<int:product_id>')

