from app import db
from datetime import datetime
import uuid
import json

class EmailGenerationLog(db.Model):
    __tablename__ = 'EmailGenerationLog'
    
    LogId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    EmailTemplateId = db.Column(db.String(36), db.ForeignKey('Templates.EmailTemplateId'), nullable=False)
    GeneratedBy = db.Column(db.String(200), nullable=False)
    GenerationTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    Recipients = db.Column(db.Text, nullable=True)  # JSON array of recipient emails
    ParametersUsed = db.Column(db.Text, nullable=True)  # JSON object of parameter values
    SubjectGenerated = db.Column(db.String(1000), nullable=True)
    AttachmentIncluded = db.Column(db.Boolean, nullable=False, default=False)
    AutoSent = db.Column(db.Boolean, nullable=False, default=False)
    OutlookDraftId = db.Column(db.String(200), nullable=True)  # Microsoft Graph API draft ID
    Status = db.Column(db.String(50), nullable=False, default='SUCCESS')  # 'SUCCESS', 'FAILED', 'PENDING'
    ErrorMessage = db.Column(db.Text, nullable=True)
    
    # Relationship to Template
    template = db.relationship('Template', backref=db.backref('generation_logs', lazy='dynamic'))