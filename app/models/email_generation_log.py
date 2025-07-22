from app import db
from datetime import datetime
import uuid
import json

class EmailGenerationLog(db.Model):
    __tablename__ = 'email_generation_log'
    
    log_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_template_id = db.Column(db.String(36), db.ForeignKey('templates.email_template_id'), nullable=False)
    generated_by = db.Column(db.String(200), nullable=False)
    generation_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    recipients = db.Column(db.Text, nullable=True)  # JSON array of recipient emails
    parameters_used = db.Column(db.Text, nullable=True)  # JSON object of parameter values
    subject_generated = db.Column(db.String(1000), nullable=True)
    attachment_included = db.Column(db.Boolean, nullable=False, default=False)
    auto_sent = db.Column(db.Boolean, nullable=False, default=False)
    outlook_draft_id = db.Column(db.String(200), nullable=True)  # Microsoft Graph API draft ID
    status = db.Column(db.String(50), nullable=False, default='SUCCESS')  # 'SUCCESS', 'FAILED', 'PENDING'
    error_message = db.Column(db.Text, nullable=True)
    
    # Relationship to Template
    template = db.relationship('Template', backref=db.backref('generation_logs', lazy='dynamic'))