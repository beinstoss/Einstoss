from flask import Blueprint, request, jsonify
from app.models.application import Application
from app.models.template import Template
from app.services.auth_service import AuthService
from app import db
from datetime import datetime

applications_bp = Blueprint('applications', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@applications_bp.route('/', methods=['GET'])
def get_applications():
    """Get all applications (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        # Get all applications (including inactive ones for admin view)
        applications = Application.query.all()
        
        return jsonify({
            'Applications': [app.to_dict() for app in applications],
            'Total': len(applications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/active', methods=['GET'])
def get_active_applications():
    """Get only active applications (available to all users)"""
    try:
        # This endpoint is available to all users to see which applications are available
        applications = AuthService.get_applications()
        
        return jsonify({
            'Applications': [app.to_dict() for app in applications],
            'Total': len(applications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/accessible', methods=['GET'])
def get_accessible_applications():
    """Get applications user has access to"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Get only applications that user has access to
        accessible_apps = AuthService.get_user_applications(user_entitlements, 'read')
        
        if not accessible_apps:
            return jsonify({
                'Applications': [],
                'Total': 0
            })
        
        # Get applications with their metadata
        all_apps = AuthService.get_applications()
        
        # Filter to only show applications user has access to
        app_list = []
        for app in all_apps:
            if app.ApplicationName in accessible_apps:
                app_list.append(app.to_dict())
        
        return jsonify({
            'Applications': app_list,
            'Total': len(app_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/', methods=['POST'])
def create_application():
    """Create a new application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        data = request.get_json()
        application_name = data.get('ApplicationName')
        
        if not application_name:
            return jsonify({'error': 'ApplicationName is required'}), 400
        
        # Check if application already exists
        existing_app = Application.query.filter_by(ApplicationName=application_name).first()
        if existing_app:
            return jsonify({'error': 'Application already exists'}), 409
        
        # Get user identifier for audit trail
        created_by = request.headers.get('X-User-ID', 'unknown')
        
        application = Application(
            ApplicationName=application_name,
            CreatedBy=created_by,
            DisplayName=data.get('DisplayName', application_name),
            Description=data.get('Description'),
            IsActive=data.get('IsActive', True)
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify(application.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>', methods=['GET'])
def get_application(application_name):
    """Get specific application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        application = Application.query.filter_by(ApplicationName=application_name).first_or_404()
        return jsonify(application.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>', methods=['PUT'])
def update_application(application_name):
    """Update application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        application = Application.query.filter_by(ApplicationName=application_name).first_or_404()
        data = request.get_json()
        
        # Update fields
        application.DisplayName = data.get('DisplayName', application.DisplayName)
        application.Description = data.get('Description', application.Description)
        application.IsActive = data.get('IsActive', application.IsActive)
        application.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        application.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(application.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>', methods=['DELETE'])
def delete_application(application_name):
    """Soft delete (deactivate) application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        application = Application.query.filter_by(ApplicationName=application_name).first_or_404()
        
        # Soft delete by setting IsActive to False
        application.IsActive = False
        application.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        application.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Application deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>/activate', methods=['POST'])
def activate_application(application_name):
    """Reactivate application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        application = Application.query.filter_by(ApplicationName=application_name).first_or_404()
        
        # Reactivate by setting IsActive to True
        application.IsActive = True
        application.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        application.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(application.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>/templates/count', methods=['GET'])
def get_application_template_count(application_name):
    """Get template count for specific application (only if active and user has access)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user has access to this application
        if not AuthService.has_application_access(user_entitlements, application_name, 'read'):
            return jsonify({'error': 'Access denied to this application'}), 403
        
        count = Template.query.filter_by(ApplicationName=application_name).count()
        return jsonify({
            'ApplicationName': application_name,
            'TemplateCount': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500