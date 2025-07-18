# app/models/user_models.py

from app import db, bcrypt # Import db and bcrypt from your app initialization
from datetime import datetime

class Merchant(db.Model):
    """
    Represents the superuser (Merchant) of the inventory system.
    Responsible for adding admins and overseeing overall store performance.
    """
    __tablename__ = 'merchants' # Define table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_superuser = db.Column(db.Boolean, default=True, nullable=False) # Merchant is the superuser
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships: A merchant can have multiple admins
    admins = db.relationship('Admin', backref='merchant', lazy=True)

    def __repr__(self):
        return f'<Merchant {self.username}>'

    @property
    def password(self):
        """Prevents password from being accessed directly."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Converts merchant object to a dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_superuser': self.is_superuser,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Admin(db.Model):
    """
    Represents a Store Admin.
    Admins are added by the Merchant and manage a specific store.
    They can add/manage clerks, approve supply requests, and view reports.
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=True) # Will be added when Store model exists
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (will be defined as other models are created)
    # clerks = db.relationship('Clerk', backref='admin', lazy=True) # An admin can have multiple clerks
    # supply_requests = db.relationship('SupplyRequest', backref='admin', lazy=True) # Admin approves/declines requests

    def __repr__(self):
        return f'<Admin {self.username}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'merchant_id': self.merchant_id,
            # 'store_id': self.store_id, # Uncomment when Store model is ready
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# You will add Clerk model here later
# class Clerk(db.Model):
#     ...
