import os
import requests
from datetime import timedelta

class Config:
    # CyberArk configuration
    CYBERARK_API_URL = os.environ.get('CYBERARK_API_URL')
    CYBERARK_SAFE_NAME = os.environ.get('CYBERARK_SAFE_NAME')
    CYBERARK_OBJECT_NAME = os.environ.get('CYBERARK_OBJECT_NAME')  # SQL Server credential object
    CYBERARK_APP_ID = os.environ.get('CYBERARK_APP_ID')
    
    # SQL Server configuration
    SQL_SERVER_HOST = os.environ.get('SQL_SERVER_HOST')
    SQL_SERVER_PORT = os.environ.get('SQL_SERVER_PORT', '1433')
    SQL_SERVER_DATABASE = os.environ.get('SQL_SERVER_DATABASE')
    SQL_SERVER_USERNAME = os.environ.get('SQL_SERVER_USERNAME')
    
    @staticmethod
    def get_sql_password():
        """Fetch SQL Server password from CyberArk"""
        try:
            cyberark_url = f"{Config.CYBERARK_API_URL}/AIMWebService/api/Accounts"
            params = {
                'AppID': Config.CYBERARK_APP_ID,
                'Safe': Config.CYBERARK_SAFE_NAME,
                'Object': Config.CYBERARK_OBJECT_NAME
            }
            
            response = requests.get(cyberark_url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json().get('Content', '')
        except Exception as e:
            raise Exception(f"Failed to retrieve password from CyberArk: {str(e)}")
    
    # For development, use simple SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///emaildrafter.db')
    
    @classmethod
    def get_production_database_uri(cls):
        """Build SQL Server connection string with CyberArk password for production"""
        try:
            password = cls.get_sql_password()
            return (
                f"mssql+pyodbc://{cls.SQL_SERVER_USERNAME}:{password}@"
                f"{cls.SQL_SERVER_HOST}:{cls.SQL_SERVER_PORT}/{cls.SQL_SERVER_DATABASE}"
                f"?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            )
        except Exception as e:
            raise Exception(f"Failed to build production database URI: {e}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration for OAuth integration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    # OAuth service configuration (your internal API)
    OAUTH_VALIDATION_URL = os.environ.get('OAUTH_VALIDATION_URL')
    
    # Azure/Entra App configuration for Graph API (SSL Certificate Auth)
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
    AZURE_CERT_PATH = os.environ.get('AZURE_CERT_PATH')  # Path to .pem certificate file
    AZURE_CERT_PASSWORD = os.environ.get('AZURE_CERT_PASSWORD')  # Certificate password if any
    AZURE_CERT_THUMBPRINT = os.environ.get('AZURE_CERT_THUMBPRINT')  # Certificate thumbprint
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'https://your-frontend-domain.com']