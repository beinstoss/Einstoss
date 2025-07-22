class AuthService:
    @staticmethod
    def get_user_applications(entitlements, permission_type='read'):
        """
        Extract applications user has access to from entitlements
        
        Args:
            entitlements: List of entitlement strings
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            List of application names user has access to
        """
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
                        if app_name:
                            applications.append(app_name.upper())
        
        return list(set(applications))  # Remove duplicates
    
    @staticmethod
    def has_application_access(entitlements, application_name, permission_type='read'):
        """
        Check if user has specific permission for an application
        
        Args:
            entitlements: List of entitlement strings
            application_name: Application to check access for
            permission_type: 'read', 'write', 'admin'
        
        Returns:
            Boolean indicating if user has access
        """
        accessible_apps = AuthService.get_user_applications(entitlements, permission_type)
        return application_name.upper() in [app.upper() for app in accessible_apps]