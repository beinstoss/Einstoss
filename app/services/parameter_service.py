from app.models.parameter import Parameter
from app import db
import re
from datetime import datetime
from flask import current_app

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
            'DataType': param.DataType
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
    
    @staticmethod
    def replace_parameters_in_text(text, parameter_values, use_defaults=True):
        """
        Replace @@parameter placeholders in text with provided values
        
        Args:
            text (str): Text containing @@parameter placeholders
            parameter_values (dict): Dictionary of parameter names to values
            use_defaults (bool): Whether to use default values for missing parameters
            
        Returns:
            tuple: (processed_text, missing_parameters, replacement_log)
        """
        if not text:
            return text, [], []
        
        # Find all @@parameter patterns
        parameter_pattern = r'@@([A-Za-z][A-Za-z0-9_]*)'
        found_parameters = re.findall(parameter_pattern, text)
        
        if not found_parameters:
            return text, [], []
        
        # Get parameter definitions from database
        db_parameters = {
            param.ParameterName: param 
            for param in Parameter.query.filter_by(IsActive=True).all()
        }
        
        missing_parameters = []
        replacement_log = []
        processed_text = text
        
        # Process each unique parameter found
        for param_name in set(found_parameters):
            param_pattern = f'@@{param_name}'
            replacement_value = None
            source = None
            
            # Check if value provided in parameter_values
            if param_name in parameter_values:
                replacement_value = parameter_values[param_name]
                source = 'payload'
            # Check if parameter exists in database and use default if allowed
            elif param_name in db_parameters and use_defaults:
                db_param = db_parameters[param_name]
                if db_param.DefaultValue:
                    replacement_value = db_param.DefaultValue
                    source = 'default'
            
            # Perform replacement or track missing parameter
            if replacement_value is not None:
                # Convert value to string and handle data type formatting
                formatted_value = ParameterService._format_parameter_value(
                    replacement_value, 
                    db_parameters.get(param_name)
                )
                processed_text = processed_text.replace(param_pattern, formatted_value)
                replacement_log.append({
                    'parameter': param_name,
                    'value': formatted_value,
                    'source': source,
                    'original_value': replacement_value
                })
            else:
                missing_parameters.append(param_name)
                replacement_log.append({
                    'parameter': param_name,
                    'value': None,
                    'source': 'missing',
                    'original_value': None
                })
        
        return processed_text, missing_parameters, replacement_log
    
    @staticmethod
    def _format_parameter_value(value, parameter_definition):
        """
        Format parameter value based on its data type
        
        Args:
            value: The raw parameter value
            parameter_definition: Parameter model instance or None
            
        Returns:
            str: Formatted value as string
        """
        if value is None:
            return ''
        
        # If no parameter definition, return as string
        if not parameter_definition:
            return str(value)
        
        data_type = parameter_definition.DataType.lower() if parameter_definition.DataType else 'string'
        
        try:
            if data_type == 'date':
                # Handle date formatting
                if isinstance(value, str):
                    # Try to parse common date formats
                    try:
                        parsed_date = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        # If parsing fails, return as-is
                        return str(value)
                elif hasattr(value, 'strftime'):
                    return value.strftime('%Y-%m-%d')
                else:
                    return str(value)
            
            elif data_type == 'number':
                # Handle numeric formatting
                try:
                    # Try to format as number with appropriate precision
                    if isinstance(value, (int, float)):
                        return str(value)
                    else:
                        # Try to convert string to number
                        if '.' in str(value):
                            return str(float(value))
                        else:
                            return str(int(value))
                except (ValueError, TypeError):
                    return str(value)
            
            elif data_type == 'boolean':
                # Handle boolean formatting
                if isinstance(value, bool):
                    return 'true' if value else 'false'
                elif isinstance(value, str):
                    return 'true' if value.lower() in ['true', '1', 'yes', 'on'] else 'false'
                else:
                    return 'true' if value else 'false'
            
            else:  # string or unknown type
                return str(value)
                
        except Exception as e:
            # If any formatting fails, log warning and return as string
            current_app.logger.warning(f"Failed to format parameter value: {e}")
            return str(value)
    
    @staticmethod
    def get_template_parameters(template_text):
        """
        Extract all @@parameter references from template text
        
        Args:
            template_text (str): Text to extract parameters from
            
        Returns:
            list: List of unique parameter names found
        """
        if not template_text:
            return []
        
        parameter_pattern = r'@@([A-Za-z][A-Za-z0-9_]*)'
        found_parameters = re.findall(parameter_pattern, template_text)
        
        return list(set(found_parameters))
    
    @staticmethod
    def prepare_email_content(subject_template, body_template, parameter_values, use_defaults=True):
        """
        Process email templates and replace parameters
        
        Args:
            subject_template (str): Email subject template
            body_template (str): Email body template
            parameter_values (dict): Parameter values to substitute
            use_defaults (bool): Whether to use default values for missing parameters
            
        Returns:
            dict: Processing results with subject, body, and metadata
        """
        # Process subject
        processed_subject, missing_subject, subject_log = ParameterService.replace_parameters_in_text(
            subject_template, parameter_values, use_defaults
        )
        
        # Process body
        processed_body, missing_body, body_log = ParameterService.replace_parameters_in_text(
            body_template, parameter_values, use_defaults
        )
        
        # Combine missing parameters
        all_missing = list(set(missing_subject + missing_body))
        
        return {
            'subject': processed_subject,
            'body': processed_body,
            'missing_parameters': all_missing,
            'replacement_log': {
                'subject': subject_log,
                'body': body_log
            },
            'has_missing_parameters': len(all_missing) > 0
        }