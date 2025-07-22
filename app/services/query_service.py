from app.models.template import Template
from app import db
from sqlalchemy import and_, or_, not_, text
from sqlalchemy.exc import SQLAlchemyError
import re
from datetime import datetime

class QueryService:
    """Service for handling dynamic template queries with filtering"""
    
    # Allowed fields for filtering (security measure)
    ALLOWED_FIELDS = {
        'application_name': Template.application_name,
        'ssg_team': Template.ssg_team,
        'recipient_type': Template.recipient_type,
        'template_name': Template.template_name,
        'sender': Template.sender,
        'subject': Template.subject,
        'body': Template.body,
        'auto_send': Template.auto_send,
        'data_as_attachment': Template.data_as_attachment,
        'created_by': Template.created_by,
        'creation_time': Template.creation_time,
        'modified_by': Template.modified_by,
        'modified_time': Template.modified_time
    }
    
    # Allowed operators for filtering
    ALLOWED_OPERATORS = {
        'eq': '=',           # Equal
        'ne': '!=',          # Not equal
        'gt': '>',           # Greater than
        'gte': '>=',         # Greater than or equal
        'lt': '<',           # Less than
        'lte': '<=',         # Less than or equal
        'like': 'LIKE',      # Like (contains)
        'ilike': 'ILIKE',    # Case insensitive like
        'in': 'IN',          # In list
        'not_in': 'NOT IN',  # Not in list
        'is_null': 'IS NULL',     # Is null
        'is_not_null': 'IS NOT NULL'  # Is not null
    }
    
    @classmethod
    def query_templates(cls, user_entitlements, filters=None, sort_by=None, 
                       sort_order='asc', page=1, page_size=50):
        """
        Query templates with dynamic filtering based on user entitlements
        
        Args:
            user_entitlements: List of user entitlements
            filters: Dictionary of filter conditions
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            page: Page number (1-based)
            page_size: Number of items per page
        """
        try:
            # Get applications user has read access to
            from app.services.auth_service import AuthService
            accessible_apps = AuthService.get_user_applications(user_entitlements, 'read')
            
            if not accessible_apps:
                return {
                    'data': [],
                    'total': 0,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': 0
                }
            
            # Start with base query filtered by accessible applications
            query = Template.query.filter(Template.application_name.in_(accessible_apps))
            
            # Apply dynamic filters
            if filters:
                query = cls._apply_filters(query, filters)
            
            # Apply sorting
            if sort_by and sort_by in cls.ALLOWED_FIELDS:
                field = cls.ALLOWED_FIELDS[sort_by]
                if sort_order.lower() == 'desc':
                    query = query.order_by(field.desc())
                else:
                    query = query.order_by(field.asc())
            else:
                # Default sorting
                query = query.order_by(Template.creation_time.desc())
            
            # Get total count before pagination
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            # Execute query
            templates = query.all()
            
            return {
                'data': [template.to_dict() for template in templates],
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'filters_applied': filters,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    @classmethod
    def _apply_filters(cls, query, filters):
        """Apply dynamic filters to the query"""
        conditions = []
        
        for filter_item in filters:
            if not isinstance(filter_item, dict):
                continue
                
            field = filter_item.get('field')
            operator = filter_item.get('operator', 'eq')
            value = filter_item.get('value')
            
            # Validate field and operator
            if field not in cls.ALLOWED_FIELDS or operator not in cls.ALLOWED_OPERATORS:
                continue
            
            # Get SQLAlchemy field
            db_field = cls.ALLOWED_FIELDS[field]
            
            # Build condition based on operator
            condition = cls._build_condition(db_field, operator, value)
            if condition is not None:
                conditions.append(condition)
        
        # Apply conditions with AND logic by default
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query
    
    @classmethod
    def _build_condition(cls, field, operator, value):
        """Build individual filter condition"""
        try:
            if operator == 'eq':
                return field == value
            elif operator == 'ne':
                return field != value
            elif operator == 'gt':
                return field > value
            elif operator == 'gte':
                return field >= value
            elif operator == 'lt':
                return field < value
            elif operator == 'lte':
                return field <= value
            elif operator == 'like':
                return field.like(f'%{value}%')
            elif operator == 'ilike':
                return field.ilike(f'%{value}%')
            elif operator == 'in':
                if isinstance(value, list):
                    return field.in_(value)
            elif operator == 'not_in':
                if isinstance(value, list):
                    return ~field.in_(value)
            elif operator == 'is_null':
                return field.is_(None)
            elif operator == 'is_not_null':
                return field.isnot(None)
            
            return None
        except Exception:
            return None
    
    @classmethod
    def get_field_metadata(cls):
        """Get metadata about queryable fields"""
        return {
            'allowed_fields': list(cls.ALLOWED_FIELDS.keys()),
            'allowed_operators': list(cls.ALLOWED_OPERATORS.keys()),
            'operator_descriptions': {
                'eq': 'Equal to',
                'ne': 'Not equal to',
                'gt': 'Greater than',
                'gte': 'Greater than or equal to',
                'lt': 'Less than',
                'lte': 'Less than or equal to',
                'like': 'Contains (case sensitive)',
                'ilike': 'Contains (case insensitive)',
                'in': 'In list of values',
                'not_in': 'Not in list of values',
                'is_null': 'Is null/empty',
                'is_not_null': 'Is not null/empty'
            },
            'field_types': {
                'application_name': 'string',
                'ssg_team': 'string',
                'recipient_type': 'string',
                'template_name': 'string',
                'sender': 'string',
                'subject': 'string',
                'body': 'string',
                'auto_send': 'boolean',
                'data_as_attachment': 'boolean',
                'created_by': 'string',
                'creation_time': 'datetime',
                'modified_by': 'string',
                'modified_time': 'datetime'
            }
        }
    
    @classmethod
    def validate_filters(cls, filters):
        """Validate filter structure and content"""
        if not isinstance(filters, list):
            return False, "Filters must be a list of filter objects"
        
        for i, filter_item in enumerate(filters):
            if not isinstance(filter_item, dict):
                return False, f"Filter {i} must be an object"
            
            if 'field' not in filter_item:
                return False, f"Filter {i} missing required 'field' property"
            
            field = filter_item['field']
            operator = filter_item.get('operator', 'eq')
            
            if field not in cls.ALLOWED_FIELDS:
                return False, f"Filter {i}: '{field}' is not an allowed field"
            
            if operator not in cls.ALLOWED_OPERATORS:
                return False, f"Filter {i}: '{operator}' is not an allowed operator"
            
            # Validate value is provided for operators that need it
            if operator not in ['is_null', 'is_not_null'] and 'value' not in filter_item:
                return False, f"Filter {i}: 'value' is required for operator '{operator}'"
        
        return True, "Filters are valid"