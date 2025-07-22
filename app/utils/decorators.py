from functools import wraps
from flask import request, jsonify, g

def auth_required(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Placeholder authentication logic
        # In a real implementation, this would validate JWT tokens
        # and set g.current_user with user info and entitlements
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Mock user for development
        g.current_user = {
            'id': 'mock-user-id',
            'email': 'user@company.com',
            'entitlements': [
                'EmailDrafter>templates_RDB_read>true',
                'EmailDrafter>templates_TRADING_read>true',
                'EmailDrafter>templates_COMPLIANCE_read>true'
            ]
        }
        
        return f(*args, **kwargs)
    return decorated_function