from flask import Blueprint, request, jsonify
from app.services.parameter_service import ParameterService

parameters_bp = Blueprint('parameters', __name__)

@parameters_bp.route('/', methods=['GET'])
def get_parameters():
    """Get all active parameters"""
    try:
        parameters = ParameterService.get_all_parameters()
        return jsonify({'parameters': parameters})
    except Exception as e:
        return jsonify({'error': 'Failed to fetch parameters'}), 500

@parameters_bp.route('/autocomplete', methods=['GET'])
def get_parameter_autocomplete():
    """Get parameters for autocomplete functionality"""
    try:
        search_term = request.args.get('search', '')
        suggestions = ParameterService.get_parameter_suggestions(search_term)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': 'Failed to get parameter suggestions'}), 500

@parameters_bp.route('/validate', methods=['POST'])
def validate_parameters():
    """Validate parameters in text"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        is_valid, invalid_params = ParameterService.validate_parameters_in_text(text)
        
        return jsonify({
            'isValid': is_valid,
            'invalidParameters': invalid_params
        })
    except Exception as e:
        return jsonify({'error': 'Failed to validate parameters'}), 500