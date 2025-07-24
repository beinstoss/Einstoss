from app import db
from datetime import datetime
import uuid

class Application(db.Model):
    __tablename__ = 'Applications'
    
    ApplicationId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ApplicationName = db.Column(db.String(100), nullable=False, unique=True, index=True)
    DisplayName = db.Column(db.String(200), nullable=True)
    Description = db.Column(db.Text, nullable=True)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    CreatedBy = db.Column(db.String(200), nullable=False)
    CreationTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ModifiedBy = db.Column(db.String(200), nullable=True)
    ModifiedTime = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'ApplicationId': self.ApplicationId,
            'ApplicationName': self.ApplicationName,
            'DisplayName': self.DisplayName,
            'Description': self.Description,
            'IsActive': self.IsActive,
            'CreatedBy': self.CreatedBy,
            'CreationTime': self.CreationTime.isoformat(),
            'ModifiedBy': self.ModifiedBy,
            'ModifiedTime': self.ModifiedTime.isoformat() if self.ModifiedTime else None
        }