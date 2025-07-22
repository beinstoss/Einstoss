import requests
from flask import current_app
import json
import uuid

class OutlookService:
    @staticmethod
    def get_access_token():
        """Get access token using SSL certificate authentication"""
        try:
            token_url = f"https://login.microsoftonline.com/{current_app.config['AZURE_TENANT_ID']}/oauth2/v2.0/token"
            
            data = {
                'client_id': current_app.config['AZURE_CLIENT_ID'],
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': OutlookService._create_client_assertion(),
                'scope': 'https://graph.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            return response.json()['access_token']
        except Exception as e:
            current_app.logger.error(f"Failed to get access token: {str(e)}")
            raise
    
    @staticmethod
    def _create_client_assertion():
        """Create JWT assertion for certificate-based authentication"""
        import jwt
        import time
        from cryptography.hazmat.primitives import serialization
        
        try:
            # Load private key from certificate
            with open(current_app.config['AZURE_CERT_PATH'], 'rb') as cert_file:
                private_key = serialization.load_pem_private_key(
                    cert_file.read(),
                    password=current_app.config.get('AZURE_CERT_PASSWORD', '').encode() if current_app.config.get('AZURE_CERT_PASSWORD') else None
                )
            
            # Create JWT payload
            now = int(time.time())
            payload = {
                'aud': f"https://login.microsoftonline.com/{current_app.config['AZURE_TENANT_ID']}/oauth2/v2.0/token",
                'exp': now + 600,  # 10 minutes
                'iss': current_app.config['AZURE_CLIENT_ID'],
                'jti': str(uuid.uuid4()),
                'nbf': now,
                'sub': current_app.config['AZURE_CLIENT_ID']
            }
            
            # Create and sign JWT
            token = jwt.encode(
                payload,
                private_key,
                algorithm='RS256',
                headers={'x5t': current_app.config['AZURE_CERT_THUMBPRINT']}
            )
            
            return token
        except Exception as e:
            current_app.logger.error(f"Failed to create client assertion: {str(e)}")
            raise
    
    @staticmethod
    def create_draft(sender, subject, body, recipients=None, auto_send=False, 
                    data_as_attachment=False, attachment_data=None):
        """Create email draft using Microsoft Graph API"""
        try:
            access_token = OutlookService.get_access_token()
            
            # Prepare email content
            draft_data = {
                'subject': subject,
                'body': {
                    'contentType': 'HTML',
                    'content': body
                },
                'from': {
                    'emailAddress': {
                        'address': sender
                    }
                }
            }
            
            # Add recipients if provided
            if recipients:
                draft_data['toRecipients'] = [
                    {'emailAddress': {'address': email.strip()}} 
                    for email in recipients if email.strip()
                ]
            
            # Add attachment if specified
            if data_as_attachment and attachment_data:
                attachments = OutlookService._prepare_data_attachment(attachment_data)
                if attachments:
                    draft_data['attachments'] = attachments
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Create draft
            if auto_send:
                # Send email directly
                endpoint = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
                payload = {'message': draft_data}
                response = requests.post(endpoint, json=payload, headers=headers)
            else:
                # Create draft
                endpoint = f"https://graph.microsoft.com/v1.0/users/{sender}/messages"
                response = requests.post(endpoint, json=draft_data, headers=headers)
            
            response.raise_for_status()
            
            if auto_send:
                return {
                    'success': True,
                    'message': 'Email sent successfully',
                    'messageId': 'sent'
                }
            else:
                draft_info = response.json()
                return {
                    'success': True,
                    'message': 'Draft created successfully',
                    'draftId': draft_info.get('id'),
                    'webLink': draft_info.get('webLink')
                }
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Graph API error: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to create draft: {str(e)}'
            }
        except Exception as e:
            current_app.logger.error(f"Outlook service error: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred'
            }
    
    @staticmethod
    def _prepare_data_attachment(attachment_data):
        """Prepare data as email attachment in various formats"""
        import csv
        import io
        import json
        try:
            attachments = []
            
            if isinstance(attachment_data, dict):
                # Determine the format based on data structure or explicit format parameter
                attachment_format = attachment_data.get('format', 'json').lower()
                data_content = attachment_data.get('data', attachment_data)
                filename = attachment_data.get('filename', f'template_data.{attachment_format}')
                
                if attachment_format == 'json':
                    # JSON attachment
                    json_content = json.dumps(data_content, indent=2)
                    attachments.append({
                        '@odata.type': '#microsoft.graph.fileAttachment',
                        'name': filename,
                        'contentType': 'application/json',
                        'contentBytes': json_content.encode('utf-8').hex()
                    })
                
                elif attachment_format == 'csv':
                    # CSV attachment
                    csv_content = OutlookService._create_csv_content(data_content)
                    attachments.append({
                        '@odata.type': '#microsoft.graph.fileAttachment',
                        'name': filename,
                        'contentType': 'text/csv',
                        'contentBytes': csv_content.encode('utf-8').hex()
                    })
                
            elif isinstance(attachment_data, str):
                # Text attachment
                attachments.append({
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': 'template_data.txt',
                    'contentType': 'text/plain',
                    'contentBytes': attachment_data.encode('utf-8').hex()
                })
            
            return attachments
        except Exception as e:
            current_app.logger.error(f"Failed to prepare attachment: {str(e)}")
            return []
    
    @staticmethod
    def _create_csv_content(data):
        """Create CSV content from data"""
        import csv
        import io
        
        output = io.StringIO()
        
        if isinstance(data, list) and data:
            # List of dictionaries - create CSV with headers
            if isinstance(data[0], dict):
                fieldnames = data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                # List of values
                writer = csv.writer(output)
                for item in data:
                    writer.writerow([item] if not isinstance(item, (list, tuple)) else item)
        elif isinstance(data, dict):
            # Single dictionary - write as key-value pairs
            writer = csv.writer(output)
            writer.writerow(['Key', 'Value'])
            for key, value in data.items():
                writer.writerow([key, value])
        else:
            # Simple data
            writer = csv.writer(output)
            writer.writerow(['Data'])
            writer.writerow([data])
        
        return output.getvalue()