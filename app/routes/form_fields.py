from flask import Blueprint, request, jsonify
from app.models.parameter import FormFieldConfiguration, FormFieldOption
from app.services.auth_service import AuthService
from app import db

form_fields_bp = Blueprint('form_fields', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@form_fields_bp.route('/configuration', methods=['GET'])
def get_form_configuration():
    """Get form field configuration for application (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        application = request.args.get('application')
        
        if not application:
            return jsonify({'error': 'Application parameter is required'}), 400
        
        # Check if user has access to this application
        if not AuthService.has_application_access(user_entitlements, application, 'read'):
            return jsonify({'error': 'Access denied to this application'}), 403
        
        configurations = FormFieldConfiguration.query\
                                             .filter_by(ApplicationName=application, IsActive=True)\
                                             .order_by(FormFieldConfiguration.SortOrder)\
                                             .all()
        
        return jsonify({
            'applicationName': application,
            'fields': [config.to_dict() for config in configurations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration', methods=['POST'])
def create_form_configuration():
    """Create new form field configuration (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        data = request.get_json()
        application_name = data.get('applicationName')
        
        if not application_name:
            return jsonify({'error': 'Application name is required'}), 400
        
        # Check if user can create form configs for this application (admin or write access)
        if not AuthService.is_admin(user_entitlements):
            if not AuthService.has_application_access(user_entitlements, application_name, 'write'):
                return jsonify({'error': 'Write access denied for this application'}), 403
        
        # For non-admin users, ensure application is approved
        if not AuthService.is_admin(user_entitlements):
            if not AuthService.is_application_approved(application_name):
                return jsonify({'error': 'Application is not approved'}), 403
        
        config = FormFieldConfiguration(
            ApplicationName=application_name,
            FieldName=data.get('fieldName'),
            FieldType=data.get('fieldType'),
            FieldLabel=data.get('fieldLabel'),
            IsRequired=data.get('isRequired', False),
            AllowMultiSelect=data.get('allowMultiSelect', False),
            SortOrder=data.get('sortOrder', 0),
            CreatedBy=request.headers.get('X-User-ID', 'system')
        )
        
        db.session.add(config)
        db.session.flush()  # To get the ID
        
        # Add options if provided
        options_data = data.get('options', [])
        for opt_data in options_data:
            option = FormFieldOption(
                ConfigId=config.ConfigId,
                OptionValue=opt_data.get('value'),
                OptionText=opt_data.get('text'),
                SortOrder=opt_data.get('sortOrder', 0)
            )
            db.session.add(option)
        
        db.session.commit()
        
        return jsonify(config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration/<config_id>', methods=['PUT'])
def update_form_configuration(config_id):
    """Update form field configuration (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        config = FormFieldConfiguration.query.get_or_404(config_id)
        
        # Check if user has write access to this configuration's application
        if not AuthService.is_admin(user_entitlements):
            if not AuthService.has_application_access(user_entitlements, config.ApplicationName, 'write'):
                return jsonify({'error': 'Write access denied for this application'}), 403
        
        data = request.get_json()
        
        # Update configuration fields
        config.FieldLabel = data.get('fieldLabel', config.FieldLabel)
        config.IsRequired = data.get('isRequired', config.IsRequired)
        config.AllowMultiSelect = data.get('allowMultiSelect', config.AllowMultiSelect)
        config.SortOrder = data.get('sortOrder', config.SortOrder)
        config.IsActive = data.get('isActive', config.IsActive)
        
        # Update options if provided
        if 'options' in data:
            # Remove existing options
            FormFieldOption.query.filter_by(ConfigId=config_id).delete()
            
            # Add new options
            for opt_data in data['options']:
                option = FormFieldOption(
                    ConfigId=config_id,
                    OptionValue=opt_data.get('value'),
                    OptionText=opt_data.get('text'),
                    SortOrder=opt_data.get('sortOrder', 0)
                )
                db.session.add(option)
        
        db.session.commit()
        
        return jsonify(config.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration/<config_id>', methods=['DELETE'])
def delete_form_configuration(config_id):
    """Delete form field configuration (only for approved/active applications)"""
    try:
        user_entitlements = get_user_entitlements()
        config = FormFieldConfiguration.query.get_or_404(config_id)
        
        # Check if user has write access to this configuration's application
        if not AuthService.is_admin(user_entitlements):
            if not AuthService.has_application_access(user_entitlements, config.ApplicationName, 'write'):
                return jsonify({'error': 'Write access denied for this application'}), 403
        
        # Soft delete by setting IsActive to False
        config.IsActive = False
        db.session.commit()
        
        return jsonify({'message': 'Configuration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500