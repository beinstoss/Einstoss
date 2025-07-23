from flask import Blueprint, request, jsonify
from app.models.template import Template
from app.services.auth_service import AuthService
from app import db

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
    """Get approved and active applications user has access to"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Get only approved applications that user has access to
        accessible_apps = AuthService.get_user_applications(user_entitlements, 'read')
        
        if not accessible_apps:
            return jsonify({
                'applications': [],
                'total': 0
            })
        
        # Get approved applications with their metadata
        approved_apps = AuthService.get_approved_applications()
        
        # Filter to only show applications user has access to
        app_list = []
        for app in approved_apps:
            if app.ApplicationName in accessible_apps:
                app_list.append({
                    'name': app.ApplicationName,
                    'displayName': app.DisplayName or app.ApplicationName,
                    'description': app.Description
                })
        
        return jsonify({
            'applications': app_list,
            'total': len(app_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>/templates/count', methods=['GET'])
def get_application_template_count(application_name):
    """Get template count for specific application (only if approved and user has access)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user has access to this application
        if not AuthService.has_application_access(user_entitlements, application_name, 'read'):
            return jsonify({'error': 'Access denied to this application'}), 403
        
        count = Template.query.filter_by(ApplicationName=application_name).count()
        return jsonify({
            'applicationName': application_name,
            'templateCount': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500