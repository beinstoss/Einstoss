from flask import Blueprint, request, jsonify
from app.models.approved_application import ApprovedApplication
from app.services.auth_service import AuthService
from app import db
from datetime import datetime

approved_applications_bp = Blueprint('approved_applications', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    # This might come from JWT token or request headers
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@approved_applications_bp.route('/', methods=['GET'])
def get_approved_applications():
    """Get all approved applications (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        # Get all approved applications (including inactive ones for admin view)
        applications = ApprovedApplication.query.all()
        
        return jsonify({
            'applications': [app.to_dict() for app in applications],
            'total': len(applications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/active', methods=['GET'])
def get_active_approved_applications():
    """Get only active approved applications (available to all users)"""
    try:
        # This endpoint is available to all users to see which applications are available
        applications = AuthService.get_approved_applications()
        
        return jsonify({
            'applications': [app.to_dict() for app in applications],
            'total': len(applications)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/', methods=['POST'])
def create_approved_application():
    """Create a new approved application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        data = request.get_json()
        application_name = data.get('applicationName')
        
        if not application_name:
            return jsonify({'error': 'Application name is required'}), 400
        
        # Check if application already exists
        existing_app = ApprovedApplication.query.filter_by(ApplicationName=application_name).first()
        if existing_app:
            return jsonify({'error': 'Application already exists'}), 409
        
        # Get user identifier for audit trail
        approved_by = request.headers.get('X-User-ID', 'unknown')
        
        approved_app = ApprovedApplication(
            ApplicationName=application_name,
            ApprovedBy=approved_by,
            DisplayName=data.get('displayName', application_name),
            Description=data.get('description'),
            IsActive=data.get('isActive', True)
        )
        
        db.session.add(approved_app)
        db.session.commit()
        
        return jsonify(approved_app.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/<application_name>', methods=['GET'])
def get_approved_application(application_name):
    """Get specific approved application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        approved_app = ApprovedApplication.query.get_or_404(application_name)
        return jsonify(approved_app.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/<application_name>', methods=['PUT'])
def update_approved_application(application_name):
    """Update approved application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        approved_app = ApprovedApplication.query.get_or_404(application_name)
        data = request.get_json()
        
        # Update fields
        approved_app.DisplayName = data.get('displayName', approved_app.DisplayName)
        approved_app.Description = data.get('description', approved_app.Description)
        approved_app.IsActive = data.get('isActive', approved_app.IsActive)
        approved_app.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        approved_app.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(approved_app.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/<application_name>', methods=['DELETE'])
def delete_approved_application(application_name):
    """Soft delete (deactivate) approved application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        approved_app = ApprovedApplication.query.get_or_404(application_name)
        
        # Soft delete by setting IsActive to False
        approved_app.IsActive = False
        approved_app.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        approved_app.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Application deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@approved_applications_bp.route('/<application_name>/activate', methods=['POST'])
def activate_approved_application(application_name):
    """Reactivate approved application (admin only)"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check admin privileges
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
        
        approved_app = ApprovedApplication.query.get_or_404(application_name)
        
        # Reactivate by setting IsActive to True
        approved_app.IsActive = True
        approved_app.ModifiedBy = request.headers.get('X-User-ID', 'unknown')
        approved_app.ModifiedTime = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(approved_app.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500