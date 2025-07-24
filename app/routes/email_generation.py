from flask import Blueprint, request, jsonify
from app.models.template import Template
from app.models.email_generation_log import EmailGenerationLog
from app.services.parameter_service import ParameterService
from app.services.outlook_service import OutlookService
from app.services.auth_service import AuthService
from app import db
import uuid
from datetime import datetime
import json

email_generation_bp = Blueprint('email_generation', __name__)

def get_user_entitlements():
    """
    Extract user entitlements from request headers or JWT token
    For now, return empty list - this should be implemented based on your auth system
    """
    # TODO: Implement based on your authentication system
    return request.headers.get('X-User-Entitlements', '').split(',') if request.headers.get('X-User-Entitlements') else []

@email_generation_bp.route('/templates/<template_id>/generate', methods=['POST'])
def generate_email(template_id):
    """
    Generate email draft from template with parameter substitution
    
    Expected payload:
    {
        "recipients": ["email@example.com"],
        "parameters": {
            "ClientName": "John Doe",
            "OrderId": "12345"
        },
        "auto_send": false,
        "data_as_attachment": false,
        "use_parameter_defaults": true
    }
    """
    try:
        user_entitlements = get_user_entitlements()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Get template
        template = Template.query.get_or_404(template_id)
        
        # Check if user has access to this template's application
        if not AuthService.has_application_access(user_entitlements, template.ApplicationName, 'read'):
            return jsonify({'error': 'Access denied to this application'}), 403
        
        # Extract request parameters
        recipients = data.get('recipients', [])
        parameter_values = data.get('parameters', {})
        auto_send = data.get('auto_send', template.AutoSend)
        data_as_attachment = data.get('data_as_attachment', template.DataAsAttachment)
        use_parameter_defaults = data.get('use_parameter_defaults', True)
        
        # Validate recipients
        if not recipients or not isinstance(recipients, list):
            return jsonify({'error': 'Recipients list is required'}), 400
        
        # Process email content with parameter substitution
        content_result = ParameterService.prepare_email_content(
            template.Subject,
            template.Body,
            parameter_values,
            use_parameter_defaults
        )
        
        # Check for missing required parameters (optional - can proceed with warnings)
        if content_result['has_missing_parameters']:
            # Log warning but continue with generation
            pass
        
        # Prepare attachment data if needed
        attachment_data = None
        if data_as_attachment:
            attachment_data = {
                'data': parameter_values,
                'format': 'json',
                'filename': f'template_data_{template_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
        # Create email draft using Outlook service
        outlook_result = OutlookService.create_draft(
            sender=template.Sender,
            subject=content_result['subject'],
            body=content_result['body'],
            recipients=recipients,
            auto_send=auto_send,
            data_as_attachment=data_as_attachment,
            attachment_data=attachment_data
        )
        
        # Create log entry
        log_entry = EmailGenerationLog(
            EmailTemplateId=template_id,
            GeneratedBy=request.headers.get('X-User-ID', 'system'),
            Recipients=json.dumps(recipients),
            ParametersUsed=json.dumps(parameter_values),
            SubjectGenerated=content_result['subject'],
            AttachmentIncluded=data_as_attachment,
            AutoSent=auto_send,
            OutlookDraftId=outlook_result.get('draftId') if outlook_result['success'] else None,
            Status='SUCCESS' if outlook_result['success'] else 'FAILED',
            ErrorMessage=outlook_result.get('error') if not outlook_result['success'] else None
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        # Prepare response
        response_data = {
            'success': outlook_result['success'],
            'log_id': log_entry.LogId,
            'template_id': template_id,
            'processed_content': {
                'subject': content_result['subject'],
                'body': content_result['body'][:500] + '...' if len(content_result['body']) > 500 else content_result['body']
            },
            'parameter_processing': {
                'missing_parameters': content_result['missing_parameters'],
                'replacement_log': content_result['replacement_log']
            },
            'email_details': {
                'recipients': recipients,
                'auto_sent': auto_send,
                'attachment_included': data_as_attachment
            }
        }
        
        if outlook_result['success']:
            response_data.update({
                'message': outlook_result['message'],
                'draft_id': outlook_result.get('draftId'),
                'web_link': outlook_result.get('webLink')
            })
        else:
            response_data['error'] = outlook_result['error']
            
        status_code = 200 if outlook_result['success'] else 500
        return jsonify(response_data), status_code
        
    except Exception as e:
        # Log error and create failed log entry if template was found
        error_message = str(e)
        
        try:
            if 'template' in locals():
                log_entry = EmailGenerationLog(
                    EmailTemplateId=template_id,
                    GeneratedBy=request.headers.get('X-User-ID', 'system'),
                    Recipients=json.dumps(data.get('recipients', [])) if 'data' in locals() else None,
                    ParametersUsed=json.dumps(data.get('parameters', {})) if 'data' in locals() else None,
                    Status='FAILED',
                    ErrorMessage=error_message
                )
                db.session.add(log_entry)
                db.session.commit()
        except:
            # If logging fails, continue with error response
            pass
        
        return jsonify({
            'success': False,
            'error': f'Email generation failed: {error_message}'
        }), 500

@email_generation_bp.route('/logs', methods=['GET'])
def get_generation_logs():
    """Get email generation logs with optional filtering"""
    try:
        user_entitlements = get_user_entitlements()
        
        # Get query parameters
        template_id = request.args.get('template_id')
        status = request.args.get('status')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 records
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = EmailGenerationLog.query
        
        if template_id:
            query = query.filter_by(EmailTemplateId=template_id)
        
        if status:
            query = query.filter_by(Status=status.upper())
        
        # Apply access control - only show logs for accessible applications
        accessible_apps = AuthService.get_user_applications(user_entitlements, 'read')
        if accessible_apps:
            query = query.join(Template).filter(Template.ApplicationName.in_(accessible_apps))
        else:
            # No access to any applications
            return jsonify([]), 200
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(EmailGenerationLog.GenerationTime.desc()) \
                   .offset(offset) \
                   .limit(limit) \
                   .all()
        
        # Format response
        log_data = []
        for log in logs:
            log_dict = {
                'log_id': log.LogId,
                'template_id': log.EmailTemplateId,
                'template_name': log.template.TemplateName if log.template else None,
                'generated_by': log.GeneratedBy,
                'generation_time': log.GenerationTime.isoformat(),
                'recipients': json.loads(log.Recipients) if log.Recipients else [],
                'subject_generated': log.SubjectGenerated,
                'status': log.Status,
                'auto_sent': log.AutoSent,
                'attachment_included': log.AttachmentIncluded,
                'error_message': log.ErrorMessage
            }
            log_data.append(log_dict)
        
        return jsonify({
            'logs': log_data,
            'pagination': {
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve logs: {str(e)}'
        }), 500