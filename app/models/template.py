from app import db
from datetime import datetime
import uuid

class Template(db.Model):
    __tablename__ = 'Templates'
    
    EmailTemplateId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ApplicationName = db.Column(db.String(100), nullable=False, index=True)
    SsgTeam = db.Column(db.String(200), nullable=False)
    RecipientType = db.Column(db.String(200), nullable=False)
    TemplateName = db.Column(db.String(200), nullable=False)
    Sender = db.Column(db.String(200), nullable=False)
    Subject = db.Column(db.String(1000), nullable=False)
    Body = db.Column(db.Text, nullable=False)
    AutoSend = db.Column(db.Boolean, nullable=False, default=False)
    DataAsAttachment = db.Column(db.Boolean, nullable=False, default=False)
    CreatedBy = db.Column(db.String(200), nullable=False)
    CreationTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ModifiedBy = db.Column(db.String(200), nullable=True)
    ModifiedTime = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.EmailTemplateId,
            'applicationName': self.ApplicationName,
            'ssgTeam': self.SsgTeam,
            'recipientType': self.RecipientType,
            'templateName': self.TemplateName,
            'sender': self.Sender,
            'subject': self.Subject,
            'body': self.Body,
            'autoSend': self.AutoSend,
            'dataAsAttachment': self.DataAsAttachment,
            'createdBy': self.CreatedBy,
            'creationTime': self.CreationTime.isoformat(),
            'modifiedBy': self.ModifiedBy,
            'modifiedTime': self.ModifiedTime.isoformat() if self.ModifiedTime else None
        }