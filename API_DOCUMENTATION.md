# EmailDrafter API Documentation

## Overview

The EmailDrafter API is a Flask-based REST API for managing email templates with parameter substitution, dynamic form configuration, and Microsoft Outlook integration. The system supports multi-application environments with role-based access control and comprehensive audit logging.

## Base URL
```
http://localhost:5000/api
```

## Authentication

The API uses header-based authentication with the following headers:
- `X-User-Entitlements`: Comma-separated list of user entitlements for authorization
- `X-User-ID`: User identifier for audit trail logging

### Entitlement Format
```
EmailDrafter>admin>true                           # Admin privileges
EmailDrafter>templates_{APPLICATION}_{PERMISSION}>true  # Application-specific permissions
```

Where:
- `{APPLICATION}`: Application name (e.g., RDB, TRADING, COMPLIANCE)
- `{PERMISSION}`: Permission level (read, write, admin)

## Services Overview

### 1. AuditService (`app/services/audit_service.py`)

**Purpose**: Handles comprehensive audit logging for all template operations.

**Key Methods**:
- `log_template_insert()` - Logs template creation
- `log_template_update()` - Logs template modifications with change tracking
- `log_template_delete()` - Logs template deletion
- `get_template_audit_trail()` - Retrieves audit history for specific template
- `get_recent_template_changes()` - Gets recent changes across all templates
- `get_user_template_activity()` - Gets activity for specific user

**Features**:
- Automatic change detection for updates
- Request context tracking
- User activity tracking
- Timestamp logging

### 2. AuthService (`app/services/auth_service.py`)

**Purpose**: Manages authentication, authorization, and application access control.

**Key Methods**:
- `is_admin()` - Checks admin privileges
- `get_applications()` - Gets active applications
- `is_application_active()` - Validates application active status
- `can_create_template_for_application()` - Checks template creation permissions
- `get_user_applications()` - Gets applications user has access to
- `has_application_access()` - Validates specific application access

**Features**:
- Role-based access control
- Application-level security
- Entitlement parsing and validation
- Admin privilege checking

### 3. OutlookService (`app/services/outlook_service.py`)

**Purpose**: Integrates with Microsoft Graph API for email draft creation and sending.

**Key Methods**:
- `get_access_token()` - Obtains OAuth2 access token using certificate authentication
- `create_draft()` - Creates email drafts or sends emails directly
- `_create_client_assertion()` - Creates JWT assertion for certificate-based auth
- `_prepare_data_attachment()` - Prepares data as email attachments (JSON/CSV/text)

**Features**:
- Certificate-based OAuth2 authentication
- Email draft creation via Microsoft Graph API
- Automatic email sending capability
- Multi-format data attachments (JSON, CSV, text)
- Comprehensive error handling

### 4. ParameterService (`app/services/parameter_service.py`)

**Purpose**: Manages parameter validation, replacement, and template processing with @@parameter substitution.

**Key Methods**:
- `get_all_parameters()` - Gets all active parameters
- `get_parameters_for_autocomplete()` - Provides autocomplete suggestions
- `validate_parameters_in_text()` - Validates parameter references in text
- `replace_parameters_in_text()` - Substitutes @@parameter placeholders with values
- `prepare_email_content()` - Processes complete email templates
- `get_template_parameters()` - Extracts parameter requirements from templates

**Features**:
- Parameter validation and substitution
- Data type formatting (string, number, date, boolean)
- Default value fallback
- Comprehensive replacement logging
- Autocomplete support for template editing

### 5. QueryService (`app/services/query_service.py`)

**Purpose**: Provides advanced querying capabilities with dynamic filtering, sorting, and pagination.

**Key Methods**:
- `query_templates()` - Main query method with filtering and pagination
- `get_field_metadata()` - Returns queryable field information
- `validate_filters()` - Validates filter structure and security
- `_apply_filters()` - Applies dynamic filters to queries
- `_build_condition()` - Builds individual filter conditions

**Features**:
- Dynamic filtering with multiple operators (eq, ne, gt, gte, lt, lte, like, ilike, in, not_in, is_null, is_not_null)
- Secure field whitelisting
- Pagination and sorting
- Access control integration
- Advanced query validation

## API Endpoints

### Authentication (`/api/auth`)

#### POST /login
**Status**: Placeholder for future OAuth integration
```json
{
  "message": "OAuth integration not yet implemented"
}
```

#### POST /validate
**Status**: Placeholder for token validation
```json
{
  "message": "Token validation not yet implemented"
}
```

---

### Applications (`/api/applications`)

#### GET /
**Purpose**: Get all applications (admin only)
**Authorization**: Admin privileges required
**Response**:
```json
{
  "Applications": [
    {
      "ApplicationId": "uuid",
      "ApplicationName": "RDB",
      "DisplayName": "Risk Database", 
      "Description": "Risk management application",
      "IsActive": true,
      "CreatedBy": "admin",
      "CreationTime": "2024-01-01T00:00:00",
      "ModifiedBy": null,
      "ModifiedTime": null
    }
  ],
  "Total": 1
}
```

#### GET /active
**Purpose**: Get only active applications (available to all users)
**Authorization**: None (public)
**Response**: Same as GET / but filtered to active applications only

#### GET /accessible
**Purpose**: Get applications user has access to
**Authorization**: Application read access required
**Response**:
```json
{
  "Applications": [
    {
      "ApplicationId": "uuid",
      "ApplicationName": "RDB",
      "DisplayName": "Risk Database",
      "Description": "Risk management application",
      "IsActive": true,
      "CreatedBy": "admin",
      "CreationTime": "2024-01-01T00:00:00"
    }
  ],
  "Total": 1
}
```

#### POST /
**Purpose**: Create new application
**Authorization**: Admin privileges required
**Request**:
```json
{
  "ApplicationName": "TRADING",
  "DisplayName": "Trading System",
  "Description": "Trading application",
  "IsActive": true
}
```

#### GET /{application_name}
**Purpose**: Get specific application
**Authorization**: Admin privileges required

#### PUT /{application_name}
**Purpose**: Update application
**Authorization**: Admin privileges required
**Request**:
```json
{
  "DisplayName": "Updated Trading System",
  "Description": "Updated description",
  "IsActive": true
}
```

#### DELETE /{application_name}
**Purpose**: Soft delete (deactivate) application
**Authorization**: Admin privileges required

#### POST /{application_name}/activate
**Purpose**: Reactivate application
**Authorization**: Admin privileges required

#### GET /{application_name}/templates/count
**Purpose**: Get template count for specific application
**Authorization**: Application read access required
**Response**:
```json
{
  "ApplicationName": "RDB",
  "TemplateCount": 25
}
```

---

### Email Generation (`/api/email`)

#### POST /templates/{template_id}/generate
**Purpose**: Generate email draft from template with parameter substitution
**Authorization**: Application read access required
**Request**:
```json
{
  "recipients": ["user@example.com", "admin@example.com"],
  "parameters": {
    "ClientName": "John Doe",
    "OrderId": "12345",
    "RiskLimit": "1000000"
  },
  "auto_send": false,
  "data_as_attachment": true,
  "use_parameter_defaults": true
}
```

**Response**:
```json
{
  "success": true,
  "log_id": "uuid",
  "template_id": "template-uuid",
  "processed_content": {
    "subject": "Risk Alert for John Doe - Order 12345",
    "body": "Dear John Doe, your order 12345 has exceeded the risk limit of 1000000..."
  },
  "parameter_processing": {
    "missing_parameters": [],
    "replacement_log": {
      "subject": [
        {
          "parameter": "ClientName",
          "value": "John Doe",
          "source": "payload",
          "original_value": "John Doe"
        }
      ],
      "body": [...]
    }
  },
  "email_details": {
    "recipients": ["user@example.com"],
    "auto_sent": false,
    "attachment_included": true
  },
  "message": "Draft created successfully",
  "draft_id": "outlook-draft-id",
  "web_link": "https://outlook.office.com/..."
}
```

#### GET /logs
**Purpose**: Get email generation logs with optional filtering
**Authorization**: Application read access required
**Query Parameters**:
- `template_id` (optional): Filter by template ID
- `status` (optional): Filter by status (SUCCESS, FAILED, PENDING)
- `limit` (optional): Max 100 records, default 50
- `offset` (optional): Pagination offset, default 0

**Response**:
```json
{
  "logs": [
    {
      "log_id": "uuid",
      "template_id": "template-uuid",
      "template_name": "Risk Alert Template",
      "generated_by": "user123",
      "generation_time": "2024-01-01T12:00:00",
      "recipients": ["user@example.com"],
      "subject_generated": "Risk Alert for John Doe",
      "status": "SUCCESS",
      "auto_sent": false,
      "attachment_included": true,
      "error_message": null
    }
  ],
  "pagination": {
    "total_count": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

---

### Form Fields (`/api/form-fields`)

#### GET /configuration
**Purpose**: Get form field configuration for application
**Authorization**: Application read access required
**Query Parameters**:
- `application` (required): Application name

**Response**:
```json
[
  {
    "id": "uuid",
    "applicationName": "RDB",
    "fieldName": "ssgTeam",
    "fieldType": "dropdown",
    "fieldLabel": "SSG Team",
    "isRequired": true,
    "allowMultiSelect": false,
    "sortOrder": 1,
    "isActive": true,
    "options": [
      {
        "id": "uuid",
        "value": "TEAM_A",
        "text": "Team Alpha",
        "sortOrder": 1
      }
    ]
  }
]
```

#### POST /configuration
**Purpose**: Create new form field configuration
**Authorization**: Application write access or admin required
**Request**:
```json
{
  "applicationName": "RDB",
  "fieldName": "ssgTeam",
  "fieldType": "dropdown",
  "fieldLabel": "SSG Team",
  "isRequired": true,
  "allowMultiSelect": false,
  "sortOrder": 1,
  "options": [
    {
      "value": "TEAM_A",
      "text": "Team Alpha",
      "sortOrder": 1
    }
  ]
}
```

#### PUT /configuration/{config_id}
**Purpose**: Update form field configuration
**Authorization**: Application write access or admin required

#### DELETE /configuration/{config_id}
**Purpose**: Delete form field configuration
**Authorization**: Application write access or admin required

---

### Parameters (`/api/parameters`)

#### GET /
**Purpose**: Get all active parameters
**Authorization**: None (public)
**Response**:
```json
[
  {
    "id": "uuid",
    "name": "ClientName",
    "description": "Client's full name",
    "dataType": "String",
    "defaultValue": "Unknown Client",
    "isActive": true,
    "createdBy": "admin",
    "creationTime": "2024-01-01T00:00:00"
  }
]
```

#### GET /autocomplete
**Purpose**: Get parameters for autocomplete functionality
**Authorization**: None (public)
**Query Parameters**:
- `search` (optional): Filter parameters by name

**Response**:
```json
[
  {
    "value": "ClientName",
    "label": "ClientName",
    "description": "Client's full name",
    "dataType": "String"
  }
]
```

#### POST /validate
**Purpose**: Validate parameters in text
**Authorization**: None (public)
**Request**:
```json
{
  "text": "Hello @@ClientName, your order @@OrderId is ready."
}
```

**Response**:
```json
{
  "isValid": true,
  "invalidParameters": []
}
```

---

### Query (`/api/query`)

#### GET /templates
**Purpose**: Query templates with advanced filtering
**Authorization**: Currently hardcoded (TODO: implement authentication)
**Query Parameters**:
- `filters` (optional): JSON string of filter conditions
- `sort_by` (optional): Field to sort by
- `sort_order` (optional): 'asc' or 'desc'
- `page` (optional): Page number, default 1
- `page_size` (optional): Items per page, default 50, max 200

**Example Filters**:
```json
[
  {
    "field": "application_name",
    "operator": "eq",
    "value": "RDB"
  },
  {
    "field": "template_name",
    "operator": "ilike",
    "value": "risk"
  }
]
```

**Response**:
```json
{
  "data": [
    {
      "id": "uuid",
      "applicationName": "RDB",
      "templateName": "Risk Alert",
      "subject": "Risk Alert for @@ClientName",
      "body": "Dear @@ClientName...",
      "createdBy": "admin",
      "creationTime": "2024-01-01T00:00:00"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 50,
  "total_pages": 1,
  "filters_applied": [...],
  "sort_by": "creation_time",
  "sort_order": "desc"
}
```

#### POST /templates
**Purpose**: Query templates using POST with JSON body
**Authorization**: Currently hardcoded
**Request**:
```json
{
  "filters": [...],
  "sort_by": "template_name",
  "sort_order": "asc",
  "page": 1,
  "page_size": 50
}
```

#### GET /templates/metadata
**Purpose**: Get metadata about queryable fields and operators
**Authorization**: None
**Response**:
```json
{
  "allowed_fields": ["application_name", "template_name", "subject", ...],
  "allowed_operators": ["eq", "ne", "gt", "gte", "lt", "lte", "like", "ilike", "in", "not_in", "is_null", "is_not_null"],
  "operator_descriptions": {
    "eq": "Equal to",
    "ilike": "Contains (case insensitive)",
    ...
  },
  "field_types": {
    "application_name": "string",
    "creation_time": "datetime",
    "auto_send": "boolean",
    ...
  }
}
```

#### GET /templates/count
**Purpose**: Get count of templates matching filter criteria
**Authorization**: Currently hardcoded

#### GET|POST /templates/export
**Purpose**: Export templates in various formats
**Authorization**: Currently hardcoded
**Query Parameters**:
- `format`: 'csv', 'json', or 'xlsx'
- `filters`: Filter conditions
- `page_size`: Up to 10,000 records for export

---

### Template Audit (`/api/audit`)

#### GET /template/{template_id}
**Purpose**: Get audit history for specific template
**Authorization**: Admin privileges required
**Query Parameters**:
- `limit` (optional): Max 200 records, default 50

**Response**:
```json
[
  {
    "id": "uuid",
    "templateId": "template-uuid",
    "action": "UPDATE",
    "userId": "user123",
    "timestamp": "2024-01-01T12:00:00",
    "ipAddress": "192.168.1.1",
    "userAgent": "Mozilla/5.0...",
    "changedFields": {
      "Subject": {
        "from": "Old Subject",
        "to": "New Subject"
      }
    }
  }
]
```

#### GET /recent
**Purpose**: Get recent template changes across all templates
**Authorization**: Admin privileges required
**Query Parameters**:
- `limit` (optional): Max 500 records, default 100
- `days` (optional): Days back to search, max 90, default 7

#### GET /user/{user_id}
**Purpose**: Get template audit activity for specific user
**Authorization**: Admin privileges or own user data
**Query Parameters**:
- `limit` (optional): Max 200 records, default 50

#### GET /statistics
**Purpose**: Get audit statistics and metrics
**Authorization**: Admin privileges required
**Query Parameters**:
- `days` (optional): Days back to analyze, max 365, default 30

**Response**:
```json
{
  "period_days": 30,
  "total_actions": 1250,
  "actions_by_type": {
    "INSERT": 45,
    "UPDATE": 180,
    "DELETE": 25
  },
  "actions_by_user": {
    "user123": 150,
    "user456": 100
  },
  "daily_activity": [
    {
      "date": "2024-01-01",
      "count": 25
    }
  ],
  "most_active_templates": [
    {
      "template_id": "uuid",
      "template_name": "Risk Alert",
      "action_count": 45
    }
  ]
}
```

#### GET /search
**Purpose**: Search audit records with various filters
**Authorization**: Admin privileges required
**Query Parameters**:
- `templateId`, `userId`, `action`, `applicationName`: Search filters
- `limit` (optional): Max 1000 records, default 100
- `days` (optional): Days back to search, max 365, default 30

---

### Templates (`/api/templates`)

#### GET /
**Purpose**: Get templates with optional application filter
**Authorization**: Application read access required
**Query Parameters**:
- `application` (optional): Filter by application name

**Response**:
```json
[
  {
    "id": "uuid",
    "applicationName": "RDB",
    "ssgTeam": "Team Alpha",
    "recipientType": "Internal",
    "templateName": "Risk Alert",
    "sender": "risk@company.com",
    "subject": "Risk Alert for @@ClientName",
    "body": "Dear @@ClientName, your risk limit has been exceeded...",
    "autoSend": false,
    "dataAsAttachment": true,
    "createdBy": "admin",
    "creationTime": "2024-01-01T00:00:00",
    "modifiedBy": null,
    "modifiedTime": null
  }
]
```

#### POST /
**Purpose**: Create a new template
**Authorization**: Application write access required, application must be approved
**Request**:
```json
{
  "applicationName": "RDB",
  "ssgTeam": "Team Alpha",
  "recipientType": "Internal",
  "templateName": "Risk Alert",
  "sender": "risk@company.com",
  "subject": "Risk Alert for @@ClientName",
  "body": "Dear @@ClientName, your risk limit of @@RiskLimit has been exceeded...",
  "autoSend": false,
  "dataAsAttachment": true
}
```

#### GET /{template_id}
**Purpose**: Get specific template by ID
**Authorization**: Application read access required

#### PUT /{template_id}
**Purpose**: Update existing template
**Authorization**: Application write access required
**Request**: Same as POST / (excluding applicationName which cannot be changed)

#### DELETE /{template_id}
**Purpose**: Delete template
**Authorization**: Application write access required

#### POST /{template_id}/duplicate
**Purpose**: Create duplicate of existing template
**Authorization**: Application read and write access required
**Request**:
```json
{
  "templateName": "Risk Alert (Copy)"
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Descriptive error message",
  "success": false
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `403`: Forbidden (access denied)
- `404`: Not Found
- `500`: Internal Server Error

## Security Features

1. **Application-Level Access Control**: Users can only access templates for applications they have permissions for
2. **Role-Based Authorization**: Admin, read, and write permissions per application
3. **Application Approval System**: Only approved applications can have templates
4. **Comprehensive Audit Logging**: All template operations are logged with user context
5. **Input Validation**: All endpoints validate input data and parameters
6. **Secure Parameter Handling**: Parameter replacement uses whitelisted, validated parameters only

## Data Models

### Template
- `EmailTemplateId` (UUID, Primary Key)
- `ApplicationName` (String, Required, Indexed)
- `SsgTeam` (String, Required)
- `RecipientType` (String, Required)
- `TemplateName` (String, Required)
- `Sender` (String, Required)
- `Subject` (String, Required)
- `Body` (Text, Required)
- `AutoSend` (Boolean, Default: false)
- `DataAsAttachment` (Boolean, Default: false)
- `CreatedBy`, `CreationTime`, `ModifiedBy`, `ModifiedTime`

### Parameter
- `ParameterId` (UUID, Primary Key)
- `ParameterName` (String, Required, Unique, Indexed)
- `Description` (String)
- `DataType` (String: String, Date, Number, Boolean)
- `DefaultValue` (Text)
- `IsActive` (Boolean, Default: true)
- `CreatedBy`, `CreationTime`, `ModifiedBy`, `ModifiedTime`

### Application
- `ApplicationId` (UUID, Primary Key)
- `ApplicationName` (String, Required, Unique, Indexed)
- `DisplayName` (String)
- `Description` (Text)
- `IsActive` (Boolean, Default: true)
- `CreatedBy`, `CreationTime`, `ModifiedBy`, `ModifiedTime`

### EmailGenerationLog
- `LogId` (UUID, Primary Key)
- `EmailTemplateId` (UUID, Foreign Key)
- `GeneratedBy` (String, Required)
- `GenerationTime` (DateTime, Default: now)
- `Recipients` (JSON Text)
- `ParametersUsed` (JSON Text)
- `SubjectGenerated` (String)
- `AttachmentIncluded` (Boolean, Default: false)
- `AutoSent` (Boolean, Default: false)
- `OutlookDraftId` (String)
- `Status` (String: SUCCESS, FAILED, PENDING)
- `ErrorMessage` (Text)

## Integration Notes

### Microsoft Graph API
- Uses certificate-based OAuth2 authentication
- Requires Azure App Registration with appropriate Graph API permissions
- Supports both draft creation and direct email sending
- Handles various attachment formats (JSON, CSV, text)

### Parameter System
- Uses `@@ParameterName` syntax in templates
- Supports data type validation and formatting
- Fallback to default values when parameters are missing
- Comprehensive logging of parameter replacements

This API provides a complete email template management system with advanced querying, audit logging, and Microsoft Outlook integration.