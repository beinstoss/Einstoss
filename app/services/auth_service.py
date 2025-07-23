from app.models.approved_application import ApprovedApplication
from app import db

class AuthService:
    @staticmethod
    def is_admin(entitlements):
        """
        Check if user has admin privileges
        
        Args:
            entitlements: List of entitlement strings
            
        Returns:
            Boolean indicating if user has admin access
        """
        if not entitlements:
            return False
            
        return "EmailDrafter>admin>true" in entitlements
    
    @staticmethod
    def get_approved_applications():
        """
        Get list of approved and active applications
        
        Returns:
            List of ApprovedApplication objects that are active
        """
        return ApprovedApplication.query.filter_by(IsActive=True).all()
    
    @staticmethod
    def get_approved_application_names():
        """
        Get list of approved and active application names
        
        Returns:
            List of application name strings
        """
        approved_apps = AuthService.get_approved_applications()
        return [app.ApplicationName for app in approved_apps]
    
    @staticmethod
    def is_application_approved(application_name):
        """
        Check if an application is approved and active
        
        Args:
            application_name: Application name to check
            
        Returns:
            Boolean indicating if application is approved and active
        """
        approved_app = ApprovedApplication.query.filter_by(
            ApplicationName=application_name, 
            IsActive=True
        ).first()
        return approved_app is not None
    
    @staticmethod
    def can_create_template_for_application(entitlements, application_name):
        """
        Check if user can create template for given application
        
        Args:
            entitlements: List of entitlement strings
            application_name: Application name to check
            
        Returns:
            Boolean indicating if user can create templates for this application
        """
        # Admins can create templates for any application (including new ones)
        if AuthService.is_admin(entitlements):
            return True
        
        # Regular users can only create templates for approved applications
        return AuthService.is_application_approved(application_name)
    
    @staticmethod
    def get_user_applications(entitlements, permission_type='read'):
        """
        Extract applications user has access to from entitlements, filtered by approved applications
        
        Args:
            entitlements: List of entitlement strings
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            List of application names user has access to (only approved/active apps)
        """
        # Get all approved application names
        approved_app_names = AuthService.get_approved_application_names()
        
        # If no approved applications, return empty list
        if not approved_app_names:
            return []
        
        applications = []
        
        for entitlement in entitlements:
            if isinstance(entitlement, str):
                # Parse entitlement format: EmailDrafter>templates_{application}_{permission}>true
                parts = entitlement.split('>')
                if len(parts) >= 3 and parts[0] == 'EmailDrafter' and parts[2] == 'true':
                    permission_part = parts[1]
                    if permission_part.startswith('templates_') and permission_part.endswith(f'_{permission_type}'):
                        # Extract application name
                        app_name = permission_part[10:-(len(permission_type) + 1)]  # Remove 'templates_' and '_{permission_type}'
                        if app_name and app_name.upper() in [name.upper() for name in approved_app_names]:
                            applications.append(app_name.upper())
        
        return list(set(applications))  # Remove duplicates
    
    @staticmethod
    def has_application_access(entitlements, application_name, permission_type='read'):
        """
        Check if user has specific permission for an application (only for approved applications)
        
        Args:
            entitlements: List of entitlement strings
            application_name: Application to check access for
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            Boolean indicating if user has access
        """
        # First check if application is approved
        if not AuthService.is_application_approved(application_name):
            return False
            
        accessible_apps = AuthService.get_user_applications(entitlements, permission_type)
        return application_name.upper() in [app.upper() for app in accessible_apps]