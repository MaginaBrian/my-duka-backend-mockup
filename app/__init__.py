from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
cors = CORS()
migrate = Migrate()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

def create_app(config_class=Config):
    """
    Application factory function
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints (will be implemented later)
    register_blueprints(app)
    
    # Error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def register_blueprints(app):
    """
    Register all blueprints with the application
    """
    # Import and register blueprints here
    # This will be implemented when we create the model files
    pass

def register_error_handlers(app):
    """
    Register error handlers
    """
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500