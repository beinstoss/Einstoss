from flask import Blueprint, request, jsonify
from app.models.template import Template
from app import db

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/', methods=['GET'])
def get_templates():
    """Get templates with optional application filter"""
    try:
        application = request.args.get('application')
        
        if application:
            templates = Template.query.filter_by(application_name=application).all()
        else:
            templates = Template.query.all()
        
        return jsonify([template.to_dict() for template in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.get_json()
        
        template = Template(
            application_name=data.get('applicationName'),
            ssg_team=data.get('ssgTeam'),
            recipient_type=data.get('recipientType'),
            template_name=data.get('templateName'),
            sender=data.get('sender'),
            subject=data.get('subject'),
            body=data.get('body'),
            auto_send=data.get('autoSend', False),
            data_as_attachment=data.get('dataAsAttachment', False),
            created_by=data.get('createdBy', 'system')
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template by ID"""
    try:
        template = Template.query.get_or_404(template_id)
        return jsonify(template.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template"""
    try:
        template = Template.query.get_or_404(template_id)
        data = request.get_json()
        
        # Update template fields
        template.ssg_team = data.get('ssgTeam', template.ssg_team)
        template.recipient_type = data.get('recipientType', template.recipient_type)
        template.template_name = data.get('templateName', template.template_name)
        template.sender = data.get('sender', template.sender)
        template.subject = data.get('subject', template.subject)
        template.body = data.get('body', template.body)
        template.auto_send = data.get('autoSend', template.auto_send)
        template.data_as_attachment = data.get('dataAsAttachment', template.data_as_attachment)
        template.modified_by = data.get('modifiedBy', 'system')
        template.modified_time = db.func.now()
        
        db.session.commit()
        
        return jsonify(template.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        template = Template.query.get_or_404(template_id)
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@templates_bp.route('/<template_id>/duplicate', methods=['POST'])
def duplicate_template(template_id):
    """Create a duplicate of an existing template"""
    try:
        original = Template.query.get_or_404(template_id)
        data = request.get_json()
        
        # Create new template based on original
        duplicate = Template(
            application_name=original.application_name,
            ssg_team=original.ssg_team,
            recipient_type=original.recipient_type,
            template_name=data.get('templateName', f"{original.template_name} (Copy)"),
            sender=original.sender,
            subject=original.subject,
            body=original.body,
            auto_send=original.auto_send,
            data_as_attachment=original.data_as_attachment,
            created_by=data.get('createdBy', 'system')
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        return jsonify(duplicate.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500