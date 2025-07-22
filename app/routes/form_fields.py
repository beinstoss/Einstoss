from flask import Blueprint, request, jsonify
from app.models.parameter import FormFieldConfiguration, FormFieldOption
from app import db

form_fields_bp = Blueprint('form_fields', __name__)

@form_fields_bp.route('/configuration', methods=['GET'])
def get_form_configuration():
    """Get form field configuration for application"""
    try:
        application = request.args.get('application')
        if not application:
            return jsonify({'error': 'Application parameter is required'}), 400
        
        configurations = FormFieldConfiguration.query\
                                             .filter_by(application_name=application, is_active=True)\
                                             .order_by(FormFieldConfiguration.sort_order)\
                                             .all()
        
        return jsonify({
            'applicationName': application,
            'fields': [config.to_dict() for config in configurations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration', methods=['POST'])
def create_form_configuration():
    """Create new form field configuration"""
    try:
        data = request.get_json()
        
        config = FormFieldConfiguration(
            application_name=data.get('applicationName'),
            field_name=data.get('fieldName'),
            field_type=data.get('fieldType'),
            field_label=data.get('fieldLabel'),
            is_required=data.get('isRequired', False),
            allow_multi_select=data.get('allowMultiSelect', False),
            sort_order=data.get('sortOrder', 0),
            created_by=data.get('createdBy', 'system')
        )
        
        db.session.add(config)
        db.session.flush()  # To get the ID
        
        # Add options if provided
        options_data = data.get('options', [])
        for opt_data in options_data:
            option = FormFieldOption(
                config_id=config.config_id,
                option_value=opt_data.get('value'),
                option_text=opt_data.get('text'),
                sort_order=opt_data.get('sortOrder', 0)
            )
            db.session.add(option)
        
        db.session.commit()
        
        return jsonify(config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration/<config_id>', methods=['PUT'])
def update_form_configuration(config_id):
    """Update form field configuration"""
    try:
        config = FormFieldConfiguration.query.get_or_404(config_id)
        data = request.get_json()
        
        # Update configuration fields
        config.field_label = data.get('fieldLabel', config.field_label)
        config.is_required = data.get('isRequired', config.is_required)
        config.allow_multi_select = data.get('allowMultiSelect', config.allow_multi_select)
        config.sort_order = data.get('sortOrder', config.sort_order)
        config.is_active = data.get('isActive', config.is_active)
        
        # Update options if provided
        if 'options' in data:
            # Remove existing options
            FormFieldOption.query.filter_by(config_id=config_id).delete()
            
            # Add new options
            for opt_data in data['options']:
                option = FormFieldOption(
                    config_id=config_id,
                    option_value=opt_data.get('value'),
                    option_text=opt_data.get('text'),
                    sort_order=opt_data.get('sortOrder', 0)
                )
                db.session.add(option)
        
        db.session.commit()
        
        return jsonify(config.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@form_fields_bp.route('/configuration/<config_id>', methods=['DELETE'])
def delete_form_configuration(config_id):
    """Delete form field configuration"""
    try:
        config = FormFieldConfiguration.query.get_or_404(config_id)
        
        # Soft delete by setting is_active to False
        config.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Configuration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500