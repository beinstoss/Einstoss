from app import db
from datetime import datetime
import uuid

class ApprovedApplication(db.Model):
    __tablename__ = 'ApprovedApplications'
    
    ApplicationName = db.Column(db.String(100), primary_key=True)
    ApprovedBy = db.Column(db.String(200), nullable=False)
    ApprovalTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    DisplayName = db.Column(db.String(200), nullable=True)
    Description = db.Column(db.Text, nullable=True)
    ModifiedBy = db.Column(db.String(200), nullable=True)
    ModifiedTime = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'applicationName': self.ApplicationName,
            'approvedBy': self.ApprovedBy,
            'approvalTime': self.ApprovalTime.isoformat(),
            'isActive': self.IsActive,
            'displayName': self.DisplayName,
            'description': self.Description,
            'modifiedBy': self.ModifiedBy,
            'modifiedTime': self.ModifiedTime.isoformat() if self.ModifiedTime else None
        }