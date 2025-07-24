from flask import Blueprint, request, jsonify
from app.models.template_audit import TemplateAudit
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from datetime import datetime, timedelta
from app import db

template_audit_bp = Blueprint('template_audit', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@template_audit_bp.route('/template/<template_id>', methods=['GET'])
def get_template_audit_history(template_id):
    """Get audit history for a specific template"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user is admin or has read access to templates
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required for audit access.'}), 403
        
        limit = int(request.args.get('limit', 50))
        if limit > 200:  # Prevent excessive queries
            limit = 200
        
        audit_records = AuditService.get_template_audit_trail(template_id, limit)
        
        return jsonify({
            'templateId': template_id,
            'auditHistory': [record.to_dict() for record in audit_records],
            'total': len(audit_records)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_audit_bp.route('/recent', methods=['GET'])
def get_recent_template_changes():
    """Get recent template changes across all templates"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user is admin
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required for audit access.'}), 403
        
        limit = int(request.args.get('limit', 100))
        if limit > 500:  # Prevent excessive queries
            limit = 500
        
        # Optional date filtering
        days_back = int(request.args.get('days', 30))
        if days_back > 365:  # Prevent excessive date ranges
            days_back = 365
        
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        audit_records = db.session.query(TemplateAudit)\
                                 .filter(TemplateAudit.AuditTimestamp >= since_date)\
                                 .order_by(TemplateAudit.AuditTimestamp.desc())\
                                 .limit(limit).all()
        
        return jsonify({
            'recentChanges': [record.to_dict() for record in audit_records],
            'total': len(audit_records),
            'sinceDate': since_date.isoformat(),
            'daysBack': days_back
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_audit_bp.route('/user/<user_id>', methods=['GET'])
def get_user_template_activity(user_id):
    """Get template audit activity for a specific user"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user is admin or requesting their own activity
        current_user = request.headers.get('X-User-ID', 'unknown')
        if not AuthService.is_admin(user_entitlements) and current_user != user_id:
            return jsonify({'error': 'Access denied. Can only view your own activity or admin required.'}), 403
        
        limit = int(request.args.get('limit', 50))
        if limit > 200:  # Prevent excessive queries
            limit = 200
        
        audit_records = AuditService.get_user_template_activity(user_id, limit)
        
        return jsonify({
            'userId': user_id,
            'activityHistory': [record.to_dict() for record in audit_records],
            'total': len(audit_records)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_audit_bp.route('/statistics', methods=['GET'])
def get_audit_statistics():
    """Get audit statistics and metrics"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user is admin
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required for audit statistics.'}), 403
        
        days_back = int(request.args.get('days', 30))
        if days_back > 365:
            days_back = 365
        
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get statistics
        total_changes = db.session.query(TemplateAudit)\
                                 .filter(TemplateAudit.AuditTimestamp >= since_date)\
                                 .count()
        
        # Changes by action type
        action_stats = db.session.query(TemplateAudit.AuditAction, db.func.count(TemplateAudit.AuditId))\
                                .filter(TemplateAudit.AuditTimestamp >= since_date)\
                                .group_by(TemplateAudit.AuditAction)\
                                .all()
        
        # Most active users
        user_stats = db.session.query(TemplateAudit.AuditUser, db.func.count(TemplateAudit.AuditId))\
                              .filter(TemplateAudit.AuditTimestamp >= since_date)\
                              .group_by(TemplateAudit.AuditUser)\
                              .order_by(db.func.count(TemplateAudit.AuditId).desc())\
                              .limit(10).all()
        
        # Daily activity
        daily_stats = db.session.query(
            db.func.date(TemplateAudit.AuditTimestamp).label('date'),
            db.func.count(TemplateAudit.AuditId).label('count')
        ).filter(TemplateAudit.AuditTimestamp >= since_date)\
         .group_by(db.func.date(TemplateAudit.AuditTimestamp))\
         .order_by(db.func.date(TemplateAudit.AuditTimestamp).desc())\
         .all()
        
        return jsonify({
            'period': {
                'sinceDate': since_date.isoformat(),
                'daysBack': days_back
            },
            'totalChanges': total_changes,
            'actionBreakdown': {action: count for action, count in action_stats},
            'topUsers': [{'user': user, 'changes': count} for user, count in user_stats],
            'dailyActivity': [{'date': str(date), 'changes': count} for date, count in daily_stats]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@template_audit_bp.route('/search', methods=['GET'])
def search_audit_records():
    """Search audit records with various filters"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Check if user is admin
        if not AuthService.is_admin(user_entitlements):
            return jsonify({'error': 'Access denied. Admin privileges required for audit search.'}), 403
        
        # Parse search parameters
        template_id = request.args.get('templateId')
        user_id = request.args.get('userId')
        action = request.args.get('action')
        application_name = request.args.get('ApplicationName')
        days_back = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 100))
        
        if days_back > 365:
            days_back = 365
        if limit > 500:
            limit = 500
        
        since_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Build query
        query = db.session.query(TemplateAudit)\
                         .filter(TemplateAudit.AuditTimestamp >= since_date)
        
        if template_id:
            query = query.filter(TemplateAudit.EmailTemplateId == template_id)
        
        if user_id:
            query = query.filter(TemplateAudit.AuditUser == user_id)
        
        if action:
            query = query.filter(TemplateAudit.AuditAction == action.upper())
        
        if application_name:
            # Need to join with template data to filter by application
            query = query.filter(TemplateAudit.TemplateData.like(f'%\"ApplicationName\":\"{application_name}\"%'))
        
        audit_records = query.order_by(TemplateAudit.AuditTimestamp.desc())\
                           .limit(limit).all()
        
        return jsonify({
            'searchResults': [record.to_dict() for record in audit_records],
            'total': len(audit_records),
            'filters': {
                'templateId': template_id,
                'userId': user_id,
                'action': action,
                'ApplicationName': application_name,
                'daysBack': days_back
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500