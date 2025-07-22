from flask import Blueprint, request, jsonify, make_response
from app.services.query_service import QueryService
import json

query_bp = Blueprint('query', __name__)

@query_bp.route('/templates', methods=['GET'])
def query_templates():
    """
    Query templates with advanced filtering capabilities
    
    Query Parameters:
    - filters: JSON string of filter conditions
    - sort_by: Field to sort by
    - sort_order: 'asc' or 'desc'
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)
    """
    try:
        # Get query parameters
        filters_param = request.args.get('filters')
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 50)), 200)  # Max 200 items per page
        
        # Parse filters
        filters = []
        if filters_param:
            try:
                filters = json.loads(filters_param)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters JSON format'}), 400
        
        # Validate filters
        if filters:
            is_valid, error_message = QueryService.validate_filters(filters)
            if not is_valid:
                return jsonify({'error': error_message}), 400
        
        # For now, allow access to all applications (no auth)
        user_entitlements = ['RDB', 'RISKTECH', 'OTHER']
        
        # Execute query
        result = QueryService.query_templates(
            user_entitlements=user_entitlements,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@query_bp.route('/templates', methods=['POST'])
def query_templates_post():
    """
    Query templates using POST with JSON body for complex filters
    """
    try:
        data = request.get_json() or {}
        
        # Extract parameters from JSON body
        filters = data.get('filters', [])
        sort_by = data.get('sort_by')
        sort_order = data.get('sort_order', 'asc')
        page = data.get('page', 1)
        page_size = min(data.get('page_size', 50), 200)  # Max 200 items per page
        
        # Validate filters
        if filters:
            is_valid, error_message = QueryService.validate_filters(filters)
            if not is_valid:
                return jsonify({'error': error_message}), 400
        
        # For now, allow access to all applications (no auth)
        user_entitlements = ['RDB', 'RISKTECH', 'OTHER']
        
        # Execute query
        result = QueryService.query_templates(
            user_entitlements=user_entitlements,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@query_bp.route('/templates/metadata', methods=['GET'])
def get_query_metadata():
    """
    Get metadata about queryable fields and operators
    """
    try:
        metadata = QueryService.get_field_metadata()
        
        # Add accessible applications (no auth for now)
        metadata['accessible_applications'] = ['RDB', 'RISKTECH', 'OTHER']
        
        return jsonify(metadata)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get metadata: {str(e)}'}), 500

@query_bp.route('/templates/count', methods=['GET'])
def get_templates_count():
    """
    Get count of templates matching filter criteria (without returning data)
    """
    try:
        # Get filters
        filters_param = request.args.get('filters')
        filters = []
        if filters_param:
            try:
                filters = json.loads(filters_param)
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid filters JSON format'}), 400
        
        # Validate filters
        if filters:
            is_valid, error_message = QueryService.validate_filters(filters)
            if not is_valid:
                return jsonify({'error': error_message}), 400
        
        # For now, allow access to all applications (no auth)
        user_entitlements = ['RDB', 'RISKTECH', 'OTHER']
        
        # Execute count query (page_size=0 returns only count)
        result = QueryService.query_templates(
            user_entitlements=user_entitlements,
            filters=filters,
            page=1,
            page_size=0  # Special case for count only
        )
        
        return jsonify({
            'count': result['total'],
            'filters_applied': filters
        })
        
    except Exception as e:
        return jsonify({'error': f'Count query failed: {str(e)}'}), 500

@query_bp.route('/templates/export', methods=['GET', 'POST'])
def export_templates():
    """
    Export templates matching filter criteria in various formats
    """
    try:
        # Get format
        export_format = request.args.get('format', 'json').lower()
        if export_format not in ['csv', 'json', 'xlsx']:
            return jsonify({'error': 'Invalid format. Allowed: csv, json, xlsx'}), 400
        
        # Get filters
        if request.method == 'POST':
            data = request.get_json() or {}
            filters = data.get('filters', [])
        else:
            filters_param = request.args.get('filters')
            filters = []
            if filters_param:
                try:
                    filters = json.loads(filters_param)
                except json.JSONDecodeError:
                    return jsonify({'error': 'Invalid filters JSON format'}), 400
        
        # Validate filters
        if filters:
            is_valid, error_message = QueryService.validate_filters(filters)
            if not is_valid:
                return jsonify({'error': error_message}), 400
        
        # For now, allow access to all applications (no auth)
        user_entitlements = ['RDB', 'RISKTECH', 'OTHER']
        
        # Execute query (get all results for export)
        result = QueryService.query_templates(
            user_entitlements=user_entitlements,
            filters=filters,
            page=1,
            page_size=10000  # Large page size for export
        )
        
        # Format response based on requested format
        if export_format == 'json':
            return jsonify(result)
        elif export_format == 'csv':
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            if result['data']:
                fieldnames = result['data'][0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result['data'])
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=templates_export.csv'
            return response
        
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500