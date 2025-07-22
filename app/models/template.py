from app import db
from datetime import datetime
import uuid

class Template(db.Model):
    __tablename__ = 'templates'
    
    email_template_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_name = db.Column(db.String(100), nullable=False, index=True)
    ssg_team = db.Column(db.String(200), nullable=False)
    recipient_type = db.Column(db.String(200), nullable=False)
    template_name = db.Column(db.String(200), nullable=False)
    sender = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(1000), nullable=False)
    body = db.Column(db.Text, nullable=False)
    auto_send = db.Column(db.Boolean, nullable=False, default=False)
    data_as_attachment = db.Column(db.Boolean, nullable=False, default=False)
    created_by = db.Column(db.String(200), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_by = db.Column(db.String(200), nullable=True)
    modified_time = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.email_template_id,
            'applicationName': self.application_name,
            'ssgTeam': self.ssg_team,
            'recipientType': self.recipient_type,
            'templateName': self.template_name,
            'sender': self.sender,
            'subject': self.subject,
            'body': self.body,
            'autoSend': self.auto_send,
            'dataAsAttachment': self.data_as_attachment,
            'createdBy': self.created_by,
            'creationTime': self.creation_time.isoformat(),
            'modifiedBy': self.modified_by,
            'modifiedTime': self.modified_time.isoformat() if self.modified_time else None
        }