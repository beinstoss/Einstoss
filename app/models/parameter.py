from app import db
from datetime import datetime
import uuid

class Parameter(db.Model):
    __tablename__ = 'Parameters'
    
    ParameterId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ParameterName = db.Column(db.String(100), nullable=False, unique=True, index=True)
    Description = db.Column(db.String(500), nullable=True)
    DataType = db.Column(db.String(50), nullable=False)  # String, Date, Number, Boolean
    DefaultValue = db.Column(db.Text, nullable=True)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    CreatedBy = db.Column(db.String(200), nullable=False)
    CreationTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ModifiedBy = db.Column(db.String(200), nullable=True)
    ModifiedTime = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'Id': self.ParameterId,
            'Name': self.ParameterName,
            'Description': self.Description,
            'DataType': self.DataType,
            'DefaultValue': self.DefaultValue,
            'IsActive': self.IsActive,
            'CreatedBy': self.CreatedBy,
            'CreationTime': self.CreationTime.isoformat(),
            'ModifiedBy': self.ModifiedBy,
            'ModifiedTime': self.ModifiedTime.isoformat() if self.ModifiedTime else None
        }

class FormFieldConfiguration(db.Model):
    __tablename__ = 'FormFieldConfigurations'
    
    ConfigId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ApplicationName = db.Column(db.String(100), nullable=False, index=True)
    FieldName = db.Column(db.String(100), nullable=False)
    FieldType = db.Column(db.String(50), nullable=False)  # dropdown, text, textarea, checkbox
    FieldLabel = db.Column(db.String(200), nullable=False)
    IsRequired = db.Column(db.Boolean, nullable=False, default=False)
    AllowMultiSelect = db.Column(db.Boolean, nullable=False, default=False)
    SortOrder = db.Column(db.Integer, nullable=False, default=0)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    CreatedBy = db.Column(db.String(200), nullable=False)
    CreationTime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to options
    options = db.relationship('FormFieldOption', backref='configuration', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('ApplicationName', 'FieldName', 
                          name='uq_formfieldconfig_app_field'),
    )
    
    def to_dict(self):
        return {
            'Id': self.ConfigId,
            'ApplicationName': self.ApplicationName,
            'FieldName': self.FieldName,
            'FieldType': self.FieldType,
            'FieldLabel': self.FieldLabel,
            'IsRequired': self.IsRequired,
            'AllowMultiSelect': self.AllowMultiSelect,
            'SortOrder': self.SortOrder,
            'IsActive': self.IsActive,
            'options': [option.to_dict() for option in self.options.filter_by(IsActive=True).order_by('SortOrder')]
        }

class FormFieldOption(db.Model):
    __tablename__ = 'FormFieldOptions'
    
    OptionId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ConfigId = db.Column(db.String(36), db.ForeignKey('FormFieldConfigurations.ConfigId'), nullable=False)
    OptionValue = db.Column(db.String(500), nullable=False)
    OptionText = db.Column(db.String(500), nullable=False)
    SortOrder = db.Column(db.Integer, nullable=False, default=0)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    
    def to_dict(self):
        return {
            'Id': self.OptionId,
            'Value': self.OptionValue,
            'Text': self.OptionText,
            'SortOrder': self.SortOrder
        }