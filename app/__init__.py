from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.templates import templates_bp
    from app.routes.applications import applications_bp
    from app.routes.parameters import parameters_bp
    from app.routes.form_fields import form_fields_bp
    from app.routes.query import query_bp
    from app.routes.template_audit import template_audit_bp
    from app.routes.email_generation import email_generation_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(parameters_bp, url_prefix='/api/parameters')
    app.register_blueprint(form_fields_bp, url_prefix='/api/form-fields')
    app.register_blueprint(query_bp, url_prefix='/api/query')
    app.register_blueprint(template_audit_bp, url_prefix='/api/audit')
    app.register_blueprint(email_generation_bp, url_prefix='/api/email')
    
    return app