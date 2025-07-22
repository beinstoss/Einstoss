from app import db
from datetime import datetime
import uuid

class Parameter(db.Model):
    __tablename__ = 'parameters'
    
    parameter_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parameter_name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.String(500), nullable=True)
    data_type = db.Column(db.String(50), nullable=False)  # String, Date, Number, Boolean
    default_value = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String(200), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_by = db.Column(db.String(200), nullable=True)
    modified_time = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.parameter_id,
            'name': self.parameter_name,
            'description': self.description,
            'dataType': self.data_type,
            'defaultValue': self.default_value,
            'isActive': self.is_active,
            'createdBy': self.created_by,
            'creationTime': self.creation_time.isoformat(),
            'modifiedBy': self.modified_by,
            'modifiedTime': self.modified_time.isoformat() if self.modified_time else None
        }

class FormFieldConfiguration(db.Model):
    __tablename__ = 'form_field_configurations'
    
    config_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_name = db.Column(db.String(100), nullable=False, index=True)
    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)  # dropdown, text, textarea, checkbox
    field_label = db.Column(db.String(200), nullable=False)
    is_required = db.Column(db.Boolean, nullable=False, default=False)
    allow_multi_select = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.String(200), nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to options
    options = db.relationship('FormFieldOption', backref='configuration', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('application_name', 'field_name', 
                          name='uq_formfieldconfig_app_field'),
    )
    
    def to_dict(self):
        return {
            'id': self.config_id,
            'applicationName': self.application_name,
            'fieldName': self.field_name,
            'fieldType': self.field_type,
            'fieldLabel': self.field_label,
            'isRequired': self.is_required,
            'allowMultiSelect': self.allow_multi_select,
            'sortOrder': self.sort_order,
            'isActive': self.is_active,
            'options': [option.to_dict() for option in self.options.filter_by(is_active=True).order_by('sort_order')]
        }

class FormFieldOption(db.Model):
    __tablename__ = 'form_field_options'
    
    option_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_id = db.Column(db.String(36), db.ForeignKey('form_field_configurations.config_id'), nullable=False)
    option_value = db.Column(db.String(500), nullable=False)
    option_text = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    def to_dict(self):
        return {
            'id': self.option_id,
            'value': self.option_value,
            'text': self.option_text,
            'sortOrder': self.sort_order
        }