# EmailDrafter Service

A comprehensive email template management system with parameter validation, dynamic form fields, and Microsoft Graph API integration.

## Features

- **Template Management**: Create, edit, and manage email templates with parameter support
- **Parameter Validation**: Real-time validation of @@parameters in templates
- **Dynamic Form Fields**: Configurable dropdown fields with single/multi-select capabilities
- **Microsoft Graph Integration**: Create Outlook drafts and send emails automatically
- **Query API**: Advanced filtering and search capabilities
- **Security**: Entitlement-based access control and CyberArk integration
- **Export**: Templates can be exported in JSON, CSV, and Excel formats

## Architecture

### Backend (Flask)
- **Models**: SQLAlchemy models for templates, parameters, and form configurations
- **Services**: Business logic for parameter validation, query processing, and Outlook integration
- **Routes**: RESTful API endpoints with authentication and authorization
- **Security**: CyberArk integration for credential management

### Frontend (React)
- **Components**: Reusable UI components with parameter autocomplete
- **Services**: API integration with React Query for caching
- **Forms**: Dynamic form generation based on application configuration
- **Validation**: Real-time parameter validation with visual feedback

## Setup Instructions

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**
   - Configure SQL Server connection in `.env`
   - Ensure CyberArk credentials are properly configured
   - Run database migrations

4. **Run Backend**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Configuration**
   ```bash
   # Create .env.local for React environment variables
   echo "REACT_APP_API_URL=http://localhost:5000/api" > .env.local
   ```

3. **Run Frontend**
   ```bash
   npm start
   ```

## Configuration

### CyberArk Integration
Set up the following environment variables for CyberArk:
- `CYBERARK_API_URL`: CyberArk API endpoint
- `CYBERARK_SAFE_NAME`: Safe containing SQL credentials
- `CYBERARK_OBJECT_NAME`: Credential object name
- `CYBERARK_APP_ID`: Application ID for authentication

### Azure/Entra App Configuration
For Microsoft Graph API integration:
- `AZURE_TENANT_ID`: Azure tenant ID
- `AZURE_CLIENT_ID`: Application client ID
- `AZURE_CERT_PATH`: Path to certificate file
- `AZURE_CERT_THUMBPRINT`: Certificate thumbprint

### Database Schema

The application uses the following main tables:
- `Templates`: Email template storage
- `Parameters`: Valid parameter definitions
- `FormFieldConfigurations`: Dynamic form field configurations
- `FormFieldOptions`: Options for dropdown fields
- `EmailGenerationLog`: Audit log for email generation

## API Documentation

### Query Endpoints

**GET/POST /api/query/templates**
- Query templates with advanced filtering
- Supports pagination, sorting, and complex filters
- Entitlement-based access control

**GET /api/query/templates/metadata**
- Get queryable fields and operators
- Returns user's accessible applications

**GET /api/query/templates/export**
- Export templates in JSON, CSV, or Excel format

### Parameter Endpoints

**GET /api/parameters/autocomplete**
- Get parameter suggestions for autocomplete
- Supports search filtering

**POST /api/parameters/validate**
- Validate parameters in template text
- Returns validation status and invalid parameters

## Security Features

1. **Entitlement-Based Access**: Users can only access templates from authorized applications
2. **Parameter Validation**: SQL injection prevention through parameterized queries
3. **Input Sanitization**: All user inputs are validated and sanitized
4. **Credential Management**: Secure password retrieval via CyberArk
5. **Certificate Authentication**: Azure Graph API integration using SSL certificates

## Usage Examples

### Query Templates
```javascript
// Query RDB templates created in the last 30 days
const filters = [
  { field: "application_name", operator: "eq", value: "RDB" },
  { field: "creation_time", operator: "gte", value: "2024-01-01" }
];

const result = await queryService.queryTemplates(filters, "creation_time", "desc");
```

### Parameter Autocomplete
```javascript
// Get parameter suggestions
const suggestions = await parametersService.getAutocomplete("Client");
```

### Template Creation
```javascript
const templateData = {
  templateName: "Risk Alert Template",
  ssgTeam: "Risk Management",
  subject: "Risk Alert for @@Client",
  body: "Dear @@UserName, this is regarding @@RiskType..."
};

await templatesService.createTemplate("RDB", templateData);
```

## Development Notes

- The frontend uses Tailwind CSS for styling
- React Hook Form is used for form management
- Parameter autocomplete supports arrow key navigation
- Real-time parameter validation with debouncing
- Optimized to minimize useEffect usage for better performance

## Deployment

1. **Backend**: Deploy Flask app with proper WSGI server (Gunicorn, uWSGI)
2. **Frontend**: Build React app and serve with nginx or similar
3. **Database**: Ensure SQL Server is properly configured with indexes
4. **Security**: Configure firewalls, SSL certificates, and monitoring
5. **Monitoring**: Set up logging and health checks

## Contributing

1. Follow the existing code structure and patterns
2. Ensure all parameters are validated
3. Add appropriate error handling
4. Update documentation for new features
5. Test thoroughly with different user entitlements