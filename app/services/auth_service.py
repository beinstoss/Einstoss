from app.models.application import Application
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
    def get_applications():
        """
        Get list of active applications
        
        Returns:
            List of Application objects that are active
        """
        return Application.query.filter_by(IsActive=True).all()
    
    @staticmethod
    def get_application_names():
        """
        Get list of active application names
        
        Returns:
            List of application name strings
        """
        applications = AuthService.get_applications()
        return [app.ApplicationName for app in applications]
    
    @staticmethod
    def is_application_active(application_name):
        """
        Check if an application is active
        
        Args:
            application_name: Application name to check
            
        Returns:
            Boolean indicating if application is active
        """
        application = Application.query.filter_by(
            ApplicationName=application_name, 
            IsActive=True
        ).first()
        return application is not None
    
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
        
        # Regular users can only create templates for active applications
        return AuthService.is_application_active(application_name)
    
    @staticmethod
    def get_user_applications(entitlements, permission_type='read'):
        """
        Extract applications user has access to from entitlements, filtered by active applications
        
        Args:
            entitlements: List of entitlement strings
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            List of application names user has access to (only active apps)
        """
        # Get all active application names
        active_app_names = AuthService.get_application_names()
        
        # If no active applications, return empty list
        if not active_app_names:
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
                        if app_name and app_name.upper() in [name.upper() for name in active_app_names]:
                            applications.append(app_name.upper())
        
        return list(set(applications))  # Remove duplicates
    
    @staticmethod
    def has_application_access(entitlements, application_name, permission_type='read'):
        """
        Check if user has specific permission for an application (only for active applications)
        
        Args:
            entitlements: List of entitlement strings
            application_name: Application to check access for
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            Boolean indicating if user has access
        """
        # First check if application is active
        if not AuthService.is_application_active(application_name):
            return False
            
        accessible_apps = AuthService.get_user_applications(entitlements, permission_type)
        return application_name.upper() in [app.upper() for app in accessible_apps]