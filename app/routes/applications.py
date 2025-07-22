from flask import Blueprint, request, jsonify
from app.models.template import Template
from app import db

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['GET'])
def get_applications():
    """Get all available applications from templates"""
    try:
        # Get distinct application names from templates
        applications = db.session.query(Template.application_name)\
                                .distinct()\
                                .order_by(Template.application_name)\
                                .all()
        
        app_list = [{'name': app[0], 'displayName': app[0]} for app in applications]
        
        return jsonify({
            'applications': app_list,
            'total': len(app_list)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/<application_name>/templates/count', methods=['GET'])
def get_application_template_count(application_name):
    """Get template count for specific application"""
    try:
        count = Template.query.filter_by(application_name=application_name).count()
        return jsonify({
            'applicationName': application_name,
            'templateCount': count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500