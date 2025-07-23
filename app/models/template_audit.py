from app import db
from datetime import datetime
import uuid
import json

class TemplateAudit(db.Model):
    __tablename__ = 'TemplateAudit'
    
    AuditId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    EmailTemplateId = db.Column(db.String(36), nullable=False, index=True)  # Template being audited
    AuditAction = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    AuditTimestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    AuditUser = db.Column(db.String(200), nullable=False)  # User who made the change
    
    # Store the complete template data as JSON for point-in-time reconstruction
    TemplateData = db.Column(db.Text, nullable=False)  # JSON snapshot of template
    
    # Store specific field changes for UPDATE operations
    ChangedFields = db.Column(db.Text, nullable=True)  # JSON of field changes
    
    # Additional context
    UserAgent = db.Column(db.String(500), nullable=True)  # Browser/client info
    IpAddress = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    SessionId = db.Column(db.String(100), nullable=True)  # Session identifier
    
    def to_dict(self):
        """Convert audit record to dictionary"""
        return {
            'auditId': self.AuditId,
            'emailTemplateId': self.EmailTemplateId,
            'auditAction': self.AuditAction,
            'auditTimestamp': self.AuditTimestamp.isoformat(),
            'auditUser': self.AuditUser,
            'templateData': json.loads(self.TemplateData) if self.TemplateData else None,
            'changedFields': json.loads(self.ChangedFields) if self.ChangedFields else None,
            'userAgent': self.UserAgent,
            'ipAddress': self.IpAddress,
            'sessionId': self.SessionId
        }
    
    @staticmethod
    def create_audit_record(template, action, user, changed_fields=None, request_context=None):
        """
        Create an audit record for a template change
        
        Args:
            template: Template object being audited
            action: 'INSERT', 'UPDATE', or 'DELETE'
            user: User making the change
            changed_fields: Dictionary of field changes (for UPDATE only)
            request_context: Flask request object for additional context
        """
        # Create template data snapshot
        template_data = {
            'EmailTemplateId': template.EmailTemplateId,
            'ApplicationName': template.ApplicationName,
            'SsgTeam': template.SsgTeam,
            'RecipientType': template.RecipientType,
            'TemplateName': template.TemplateName,
            'Sender': template.Sender,
            'Subject': template.Subject,
            'Body': template.Body,
            'AutoSend': template.AutoSend,
            'DataAsAttachment': template.DataAsAttachment,
            'CreatedBy': template.CreatedBy,
            'CreationTime': template.CreationTime.isoformat() if template.CreationTime else None,
            'ModifiedBy': template.ModifiedBy,
            'ModifiedTime': template.ModifiedTime.isoformat() if template.ModifiedTime else None
        }
        
        # Extract request context if available
        user_agent = None
        ip_address = None
        session_id = None
        
        if request_context:
            user_agent = request_context.headers.get('User-Agent')
            ip_address = request_context.remote_addr
            session_id = request_context.headers.get('X-Session-ID')
        
        audit_record = TemplateAudit(
            EmailTemplateId=template.EmailTemplateId,
            AuditAction=action,
            AuditUser=user,
            TemplateData=json.dumps(template_data),
            ChangedFields=json.dumps(changed_fields) if changed_fields else None,
            UserAgent=user_agent,
            IpAddress=ip_address,
            SessionId=session_id
        )
        
        db.session.add(audit_record)
        return audit_record
    
    @staticmethod
    def get_template_history(template_id, limit=50):
        """Get audit history for a specific template"""
        return TemplateAudit.query.filter_by(EmailTemplateId=template_id)\
                                 .order_by(TemplateAudit.AuditTimestamp.desc())\
                                 .limit(limit).all()
    
    @staticmethod
    def get_recent_changes(limit=100):
        """Get recent template changes across all templates"""
        return TemplateAudit.query.order_by(TemplateAudit.AuditTimestamp.desc())\
                                 .limit(limit).all()
    
    @staticmethod
    def get_user_activity(user, limit=50):
        """Get audit history for a specific user"""
        return TemplateAudit.query.filter_by(AuditUser=user)\
                                 .order_by(TemplateAudit.AuditTimestamp.desc())\
                                 .limit(limit).all()