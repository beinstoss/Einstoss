#!/usr/bin/env python3
"""
Script to add test data to the Templates model for UI testing
"""

from app import create_app, db
from app.models.template import Template
from datetime import datetime

def add_test_templates():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        Template.query.delete()
        db.session.commit()
        
        # Test templates data
        test_templates = [
            {
                'ApplicationName': 'RDB',
                'SsgTeam': 'Risk Management',
                'RecipientType': 'Client',
                'TemplateName': 'Risk Alert - High Priority',
                'Sender': 'risk.alerts@company.com',
                'Subject': 'URGENT: Risk Threshold Exceeded for @@ClientName',
                'Body': '''Dear @@UserName,

This is to inform you that @@ClientName has exceeded the risk threshold of @@RiskLimit.

Current Risk Level: @@CurrentRisk
Threshold: @@RiskLimit
Date/Time: @@AlertDateTime

Please review the attached risk report and take appropriate action.

Best regards,
Risk Management Team''',
                'AutoSend': False,
                'DataAsAttachment': True,
                'CreatedBy': 'john.smith@company.com'
            },
            {
                'ApplicationName': 'RDB',
                'SsgTeam': 'Compliance',
                'RecipientType': 'Internal',
                'TemplateName': 'Daily Risk Report',
                'Sender': 'compliance@company.com',
                'Subject': 'Daily Risk Report - @@ReportDate',
                'Body': '''Risk Management Team,

Please find the daily risk report for @@ReportDate.

Summary:
- Total Positions: @@TotalPositions
- High Risk Clients: @@HighRiskCount
- Alerts Generated: @@AlertCount

The detailed report is attached.

Compliance Team''',
                'AutoSend': True,
                'DataAsAttachment': True,
                'CreatedBy': 'compliance.team@company.com'
            },
            {
                'ApplicationName': 'RISKTECH',
                'SsgTeam': 'Technology',
                'RecipientType': 'Client',
                'TemplateName': 'System Maintenance Notification',
                'Sender': 'tech.support@company.com',
                'Subject': 'Scheduled Maintenance - @@SystemName on @@MaintenanceDate',
                'Body': '''Dear @@ClientName,

We will be performing scheduled maintenance on @@SystemName.

Maintenance Window:
Start: @@StartTime
End: @@EndTime
Expected Downtime: @@Duration

During this period, @@SystemName will be unavailable.

We apologize for any inconvenience.

Technical Support Team''',
                'AutoSend': False,
                'DataAsAttachment': False,
                'CreatedBy': 'tech.admin@company.com'
            },
            {
                'ApplicationName': 'RISKTECH',
                'SsgTeam': 'Operations',
                'RecipientType': 'Internal',
                'TemplateName': 'Trade Settlement Failure',
                'Sender': 'operations@company.com',
                'Subject': 'Settlement Failure Alert - Trade @@TradeID',
                'Body': '''Operations Team,

A trade settlement failure has occurred:

Trade Details:
- Trade ID: @@TradeID
- Client: @@ClientName
- Amount: @@TradeAmount
- Settlement Date: @@SettlementDate
- Failure Reason: @@FailureReason

Please investigate and resolve immediately.

Operations Team''',
                'AutoSend': True,
                'DataAsAttachment': False,
                'CreatedBy': 'ops.manager@company.com'
            },
            {
                'ApplicationName': 'OTHER',
                'SsgTeam': 'HR',
                'RecipientType': 'Employee',
                'TemplateName': 'Welcome New Employee',
                'Sender': 'hr@company.com',
                'Subject': 'Welcome to the Team, @@EmployeeName!',
                'Body': '''Dear @@EmployeeName,

Welcome to @@CompanyName! We are excited to have you join our @@Department team.

Your first day details:
- Start Date: @@StartDate
- Location: @@OfficeLocation
- Reporting Manager: @@ManagerName
- IT Setup Time: @@ITSetupTime

Please arrive 30 minutes early for your IT setup and orientation.

We look forward to working with you!

HR Team''',
                'AutoSend': False,
                'DataAsAttachment': False,
                'CreatedBy': 'hr.admin@company.com'
            }
        ]
        
        # Add test templates to database
        for template_data in test_templates:
            template = Template(**template_data)
            db.session.add(template)
        
        db.session.commit()
        
        # Verify data was added
        total_templates = Template.query.count()
        rdb_count = Template.query.filter_by(ApplicationName='RDB').count()
        risktech_count = Template.query.filter_by(ApplicationName='RISKTECH').count()
        other_count = Template.query.filter_by(ApplicationName='OTHER').count()
        
        print(f"✅ Successfully added {total_templates} test templates:")
        print(f"   - RDB: {rdb_count}")
        print(f"   - RISKTECH: {risktech_count}")  
        print(f"   - OTHER: {other_count}")
        print("\nTest data ready for UI testing!")

if __name__ == '__main__':
    add_test_templates()