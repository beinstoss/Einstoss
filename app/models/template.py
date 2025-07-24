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
            'Id': self.EmailTemplateId,
            'ApplicationName': self.ApplicationName,
            'SsgTeam': self.SsgTeam,
            'RecipientType': self.RecipientType,
            'TemplateName': self.TemplateName,
            'Sender': self.Sender,
            'Subject': self.Subject,
            'Body': self.Body,
            'AutoSend': self.AutoSend,
            'DataAsAttachment': self.DataAsAttachment,
            'CreatedBy': self.CreatedBy,
            'CreationTime': self.CreationTime.isoformat(),
            'ModifiedBy': self.ModifiedBy,
            'ModifiedTime': self.ModifiedTime.isoformat() if self.ModifiedTime else None
        }