from flask import Blueprint, request, jsonify
from app.models.template import Template
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app import db

templates_bp = Blueprint('templates', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@templates_bp.route('/', methods=['GET'])
def get_templates():
    """Get templates with optional application filter (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        application = request.args.get('application')
        
        # Get applications user has access to (filtered by approved/active apps)
        accessible_apps = AuthService.get_user_applications(user_entitlements, 'read')
        
        if not accessible_apps:
            return jsonify([])  # No access to any applications
        
        if application:
            # Check if user has access to the specific application
            if not AuthService.has_application_access(user_entitlements, application, 'read'):
                return jsonify({'error': 'Access denied to this application'}), 403
            
            templates = Template.query.filter_by(ApplicationName=application).all()
        else:
            # Return templates only for accessible applications
            templates = Template.query.filter(Template.ApplicationName.in_(accessible_apps)).all()
        
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/', methods=['POST'])
def create_template():
    """Create a new template (with application approval validation)"""
    try:
        user_entitlements = get_user_entitlements()
        data = request.get_json()
        application_name = data.get('ApplicationName')
        
        if not application_name:
            return jsonify({'error': 'Application name is required'}), 400
        
        # Check if user can create templates for this application
        if not AuthService.can_create_template_for_application(user_entitlements, application_name):
            return jsonify({
                'error': 'Access denied. Only administrators can create templates for new applications, or the application must be approved.'
            }), 403
        
        # Check write access for non-admin users
        if not AuthService.is_admin(user_entitlements):
            if not AuthService.has_application_access(user_entitlements, application_name, 'write'):
                return jsonify({'error': 'Write access denied for this application'}), 403
        
        template = Template(
            ApplicationName=application_name,
            SsgTeam=data.get('SsgTeam'),
            RecipientType=data.get('RecipientType'),
            TemplateName=data.get('TemplateName'),
            Sender=data.get('Sender'),
            Subject=data.get('Subject'),
            Body=data.get('Body'),
            AutoSend=data.get('AutoSend', False),
            DataAsAttachment=data.get('DataAsAttachment', False),
            CreatedBy=request.headers.get('X-User-ID', 'system')
        )
        
        db.session.add(template)
        db.session.flush()  # Get the template ID before audit
        
        # Log template creation
        AuditService.log_template_insert(template)
        
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template by ID (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        template = Template.query.get_or_404(template_id)
        
        # Check if user has access to this template's application
        if not AuthService.has_application_access(user_entitlements, template.ApplicationName, 'read'):
            return jsonify({'error': 'Access denied to this application'}), 403
        
        return jsonify(template.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        template = Template.query.get_or_404(template_id)
        
        # Check if user has write access to this template's application
        if not AuthService.has_application_access(user_entitlements, template.ApplicationName, 'write'):
            return jsonify({'error': 'Write access denied for this application'}), 403
        
        data = request.get_json()
        
        # Capture original values for audit
        original_values = {
            'ApplicationName': template.ApplicationName,
            'SsgTeam': template.SsgTeam,
            'RecipientType': template.RecipientType,
            'TemplateName': template.TemplateName,
            'Sender': template.Sender,
            'Subject': template.Subject,
            'Body': template.Body,
            'AutoSend': template.AutoSend,
            'DataAsAttachment': template.DataAsAttachment
        }
        
        # Update template fields
        template.SsgTeam = data.get('SsgTeam', template.SsgTeam)
        template.RecipientType = data.get('RecipientType', template.RecipientType)
        template.TemplateName = data.get('TemplateName', template.TemplateName)
        template.Sender = data.get('Sender', template.Sender)
        template.Subject = data.get('Subject', template.Subject)
        template.Body = data.get('Body', template.Body)
        template.AutoSend = data.get('AutoSend', template.AutoSend)
        template.DataAsAttachment = data.get('DataAsAttachment', template.DataAsAttachment)
        template.ModifiedBy = request.headers.get('X-User-ID', 'system')
        template.ModifiedTime = db.func.now()
        
        # Log template update
        AuditService.log_template_update(template, original_values)
        
        db.session.commit()
        
        return jsonify(template.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        template = Template.query.get_or_404(template_id)
        
        # Check if user has write access to this template's application
        if not AuthService.has_application_access(user_entitlements, template.ApplicationName, 'write'):
            return jsonify({'error': 'Write access denied for this application'}), 403
        
        # Log template deletion before removing it
        AuditService.log_template_delete(template)
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>/duplicate', methods=['POST'])
def duplicate_template(template_id):
    """Create a duplicate of an existing template (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        original = Template.query.get_or_404(template_id)
        
        # Check if user has read access to the original template's application
        if not AuthService.has_application_access(user_entitlements, original.ApplicationName, 'read'):
            return jsonify({'error': 'Read access denied for this application'}), 403
        
        # Check if user has write access to create new template (same application)
        if not AuthService.has_application_access(user_entitlements, original.ApplicationName, 'write'):
            return jsonify({'error': 'Write access denied for this application'}), 403
        
        data = request.get_json()
        
        # Create new template based on original
        duplicate = Template(
            ApplicationName=original.ApplicationName,
            SsgTeam=original.SsgTeam,
            RecipientType=original.RecipientType,
            TemplateName=data.get('TemplateName', f"{original.TemplateName} (Copy)"),
            Sender=original.Sender,
            Subject=original.Subject,
            Body=original.Body,
            AutoSend=original.AutoSend,
            DataAsAttachment=original.DataAsAttachment,
            CreatedBy=request.headers.get('X-User-ID', 'system')
        )
        
        db.session.add(duplicate)
        db.session.flush()  # Get the duplicate ID before audit
        
        # Log duplicate template creation
        AuditService.log_template_insert(duplicate)
        
        db.session.commit()
        
        return jsonify(duplicate.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500