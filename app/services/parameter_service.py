from app.models.parameter import Parameter
from app import db
import re

class ParameterService:
    @staticmethod
    def get_all_parameters():
        """Get all active parameters"""
        parameters = Parameter.query.filter_by(IsActive=True).order_by(Parameter.ParameterName).all()
        return [param.to_dict() for param in parameters]
    
    @staticmethod
    def get_parameters_for_autocomplete(search_term=None):
        """Get parameters formatted for autocomplete dropdown"""
        query = Parameter.query.filter_by(IsActive=True)
        
        if search_term:
            query = query.filter(Parameter.ParameterName.ilike(f'%{search_term}%'))
        
        parameters = query.order_by(Parameter.ParameterName).limit(10).all()
        
        return [{
            'value': param.ParameterName,
            'label': param.ParameterName,
            'description': param.Description,
            'dataType': param.DataType
        } for param in parameters]
    
    @staticmethod
    def validate_parameters_in_text(text):
        """Validate that all @@parameters in text are valid"""
        if not text:
            return True, []
        
        # Find all @@parameter patterns
        parameter_pattern = r'@@([A-Za-z][A-Za-z0-9_]*)'
        found_parameters = re.findall(parameter_pattern, text)
        
        if not found_parameters:
            return True, []
        
        # Get all valid parameter names
        valid_parameters = {param.ParameterName for param in Parameter.query.filter_by(IsActive=True).all()}
        
        # Check for invalid parameters
        invalid_parameters = [param for param in found_parameters if param not in valid_parameters]
        
        return len(invalid_parameters) == 0, invalid_parameters
    
    @staticmethod
    def get_parameter_suggestions(partial_name):
        """Get parameter suggestions for autocomplete"""
        if not partial_name:
            return ParameterService.get_parameters_for_autocomplete()
        
        return ParameterService.get_parameters_for_autocomplete(partial_name)