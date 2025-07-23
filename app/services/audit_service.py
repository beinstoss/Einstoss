from app.models.template_audit import TemplateAudit
from app import db
from flask import request

class AuditService:
    """Service for handling template audit logging"""
    
    @staticmethod
    def log_template_insert(template, user_id=None):
        """Log template creation"""
        user = user_id or request.headers.get('X-User-ID', 'system')
        
        TemplateAudit.create_audit_record(
            template=template,
            action='INSERT',
            user=user,
            request_context=request
        )
    
    @staticmethod  
    def log_template_update(template, original_values, user_id=None):
        """
        Log template update with changed fields
        
        Args:
            template: Updated template object
            original_values: Dictionary of original field values
            user_id: User making the change
        """
        user = user_id or request.headers.get('X-User-ID', 'system')
        
        # Determine what fields changed
        changed_fields = {}
        current_values = {
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
        
        for field, current_value in current_values.items():
            original_value = original_values.get(field)
            if original_value != current_value:
                changed_fields[field] = {
                    'from': original_value,
                    'to': current_value
                }
        
        TemplateAudit.create_audit_record(
            template=template,
            action='UPDATE',
            user=user,
            changed_fields=changed_fields,
            request_context=request
        )
    
    @staticmethod
    def log_template_delete(template, user_id=None):
        """Log template deletion"""
        user = user_id or request.headers.get('X-User-ID', 'system')
        
        TemplateAudit.create_audit_record(
            template=template,
            action='DELETE',
            user=user,
            request_context=request
        )
    
    @staticmethod
    def get_template_audit_trail(template_id, limit=50):
        """Get audit trail for a specific template"""
        return TemplateAudit.get_template_history(template_id, limit)
    
    @staticmethod
    def get_recent_template_changes(limit=100):
        """Get recent changes across all templates"""
        return TemplateAudit.get_recent_changes(limit)
    
    @staticmethod
    def get_user_template_activity(user, limit=50):
        """Get template activity for a specific user"""
        return TemplateAudit.get_user_activity(user, limit)