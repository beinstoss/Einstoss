# Database Schema Documentation

This document outlines the database schema for the Einstoss application, which consists of 7 main tables across 5 model files.

## Tables Overview

- **ApprovedApplications** - Application approval and governance registry
- **Parameters** - Global parameters for dynamic content generation
- **FormFieldConfigurations** - Configuration for dynamic form fields per application
- **FormFieldOptions** - Options for dropdown/select form fields
- **Templates** - Email templates with placeholders
- **TemplateAudit** - Complete audit trail for all template changes
- **EmailGenerationLog** - Audit log of email generations

## Table Schemas

### ApprovedApplications
*File: app/models/approved_application.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ApplicationName | String(100) | PRIMARY KEY | Unique application identifier |
| ApprovedBy | String(200) | NOT NULL | Admin who approved the application |
| ApprovalTime | DateTime | NOT NULL, DEFAULT utcnow | When application was approved |
| IsActive | Boolean | NOT NULL, DEFAULT True | Active status (controls visibility) |
| DisplayName | String(200) | NULLABLE | Human-readable application name |
| Description | Text | NULLABLE | Application description |
| ModifiedBy | String(200) | NULLABLE | Last modifier identifier |
| ModifiedTime | DateTime | NULLABLE | Last modification timestamp |

**Purpose:**
- Controls which applications are available for template creation
- Only admin users can approve new applications
- Regular users can only create templates for approved/active applications
- Provides application governance and controlled rollout capability

### Parameters
*File: app/models/parameter.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ParameterId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| ParameterName | String(100) | NOT NULL, UNIQUE, INDEX | Parameter name |
| Description | String(500) | NULLABLE | Parameter description |
| DataType | String(50) | NOT NULL | Data type (String, Date, Number, Boolean) |
| DefaultValue | Text | NULLABLE | Default parameter value |
| IsActive | Boolean | NOT NULL, DEFAULT True | Active status |
| CreatedBy | String(200) | NOT NULL | Creator identifier |
| CreationTime | DateTime | NOT NULL, DEFAULT utcnow | Creation timestamp |
| ModifiedBy | String(200) | NULLABLE | Last modifier identifier |
| ModifiedTime | DateTime | NULLABLE | Last modification timestamp |

### FormFieldConfigurations
*File: app/models/parameter.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| ConfigId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| ApplicationName | String(100) | NOT NULL, INDEX | Application name |
| FieldName | String(100) | NOT NULL | Form field name |
| FieldType | String(50) | NOT NULL | Field type (dropdown, text, textarea, checkbox) |
| FieldLabel | String(200) | NOT NULL | Display label |
| IsRequired | Boolean | NOT NULL, DEFAULT False | Required field flag |
| AllowMultiSelect | Boolean | NOT NULL, DEFAULT False | Multi-select flag |
| SortOrder | Integer | NOT NULL, DEFAULT 0 | Display order |
| IsActive | Boolean | NOT NULL, DEFAULT True | Active status |
| CreatedBy | String(200) | NOT NULL | Creator identifier |
| CreationTime | DateTime | NOT NULL, DEFAULT utcnow | Creation timestamp |

**Constraints:**
- UNIQUE(ApplicationName, FieldName) - Named: uq_formfieldconfig_app_field

**Relationships:**
- One-to-many with FormFieldOptions (CASCADE DELETE)

### FormFieldOptions
*File: app/models/parameter.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| OptionId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| ConfigId | String(36) | FOREIGN KEY → FormFieldConfigurations.ConfigId, NOT NULL | Configuration reference |
| OptionValue | String(500) | NOT NULL | Option value |
| OptionText | String(500) | NOT NULL | Display text |
| SortOrder | Integer | NOT NULL, DEFAULT 0 | Display order |
| IsActive | Boolean | NOT NULL, DEFAULT True | Active status |

**Relationships:**
- Many-to-one with FormFieldConfigurations

### Templates
*File: app/models/template.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| EmailTemplateId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| ApplicationName | String(100) | NOT NULL, INDEX | Application name |
| SsgTeam | String(200) | NOT NULL | SSG team name |
| RecipientType | String(200) | NOT NULL | Recipient type |
| TemplateName | String(200) | NOT NULL | Template name |
| Sender | String(200) | NOT NULL | Sender email/identifier |
| Subject | String(1000) | NOT NULL | Email subject template |
| Body | Text | NOT NULL | Email body template |
| AutoSend | Boolean | NOT NULL, DEFAULT False | Auto-send flag |
| DataAsAttachment | Boolean | NOT NULL, DEFAULT False | Attachment flag |
| CreatedBy | String(200) | NOT NULL | Creator identifier |
| CreationTime | DateTime | NOT NULL, DEFAULT utcnow | Creation timestamp |
| ModifiedBy | String(200) | NULLABLE | Last modifier identifier |
| ModifiedTime | DateTime | NULLABLE | Last modification timestamp |

**Relationships:**
- One-to-many with EmailGenerationLog

### TemplateAudit
*File: app/models/template_audit.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| AuditId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique audit record identifier |
| EmailTemplateId | String(36) | NOT NULL, INDEX | Template being audited (not FK due to deletes) |
| AuditAction | String(20) | NOT NULL | Action performed (INSERT, UPDATE, DELETE) |
| AuditTimestamp | DateTime | NOT NULL, DEFAULT utcnow, INDEX | When the change occurred |
| AuditUser | String(200) | NOT NULL | User who made the change |
| TemplateData | Text | NOT NULL | Complete JSON snapshot of template at time of change |
| ChangedFields | Text | NULLABLE | JSON of specific field changes (UPDATE only) |
| UserAgent | String(500) | NULLABLE | Browser/client information |
| IpAddress | String(45) | NULLABLE | IP address of user (IPv4/IPv6) |
| SessionId | String(100) | NULLABLE | Session identifier for correlation |

**Purpose:**
- **Complete audit trail** for all template modifications
- **Point-in-time reconstruction** of template state
- **Change tracking** with before/after values
- **Compliance and forensic analysis** capabilities
- **User activity monitoring** and accountability

**Key Features:**
- **Immutable records** - audit entries never modified
- **JSON snapshots** - complete template state preserved
- **Rich context** - user, IP, session tracking
- **Efficient queries** - indexed by template and timestamp
- **Admin-only access** - sensitive audit data protected

### EmailGenerationLog
*File: app/models/email_generation_log.py*

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| LogId | String(36) | PRIMARY KEY, DEFAULT uuid4() | Unique identifier |
| EmailTemplateId | String(36) | FOREIGN KEY → Templates.EmailTemplateId, NOT NULL | Template reference |
| GeneratedBy | String(200) | NOT NULL | Generator identifier |
| GenerationTime | DateTime | NOT NULL, DEFAULT utcnow | Generation timestamp |
| Recipients | Text | NULLABLE | JSON array of recipient emails |
| ParametersUsed | Text | NULLABLE | JSON object of parameter values |
| SubjectGenerated | String(1000) | NULLABLE | Generated subject |
| AttachmentIncluded | Boolean | NOT NULL, DEFAULT False | Attachment included flag |
| AutoSent | Boolean | NOT NULL, DEFAULT False | Auto-sent flag |
| OutlookDraftId | String(200) | NULLABLE | Microsoft Graph API draft ID |
| Status | String(50) | NOT NULL, DEFAULT 'SUCCESS' | Status (SUCCESS, FAILED, PENDING) |
| ErrorMessage | Text | NULLABLE | Error details if failed |

**Relationships:**
- Many-to-one with Templates

## Entity Relationships

```
ApprovedApplications (standalone) - Controls application access

Parameters (standalone)

FormFieldConfigurations
├── FormFieldOptions (one-to-many, cascade delete)

Templates
├── EmailGenerationLog (one-to-many)
├── TemplateAudit (one-to-many, audit trail)
```

## Key Features

### UUID Primary Keys
All tables use UUID (36-character string) primary keys for distributed system compatibility.

### Audit Trail
Most tables include creation/modification tracking with user identifiers and timestamps.

### Soft Delete Pattern
Tables use `IsActive` boolean flags for logical deletion rather than physical deletion.

### JSON Storage
- `EmailGenerationLog.Recipients` stores recipient email arrays as JSON text
- `EmailGenerationLog.ParametersUsed` stores parameter values as JSON objects

### Application Isolation and Governance
- **Application Approval**: Only applications in `ApprovedApplications` with `IsActive=True` are accessible
- **Multi-tenancy**: Form field configurations and templates are isolated by `ApplicationName`
- **Admin Control**: Only users with `EmailDrafter>admin>true` can approve new applications
- **Graceful Deactivation**: Setting `IsActive=False` hides application without data loss

### Microsoft Graph Integration
Email generation log includes `OutlookDraftId` for integration with Microsoft Outlook via Graph API.

### Comprehensive Audit System
- **Template Changes**: Every create, update, delete operation logged in `TemplateAudit`
- **Point-in-time Recovery**: JSON snapshots enable historical state reconstruction
- **Change Attribution**: Full user context with IP, session, and user agent tracking
- **Compliance Ready**: Immutable audit trail meets regulatory requirements
- **Admin Dashboard**: Rich audit querying and analytics via `/api/audit` endpoints

## Column Naming Convention

**Pascal Case**: All database columns now use Pascal Case naming convention (e.g., `EmailTemplateId`, `ParameterName`, `CreatedBy`, `Description`, `Sender`, `Subject`, `Body`, `Recipients`, `Status`) for complete consistency and improved readability.

This uniform Pascal Case naming convention improves code maintainability, readability, and provides a consistent developer experience across all database interactions.