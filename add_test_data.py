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
                'application_name': 'RDB',
                'ssg_team': 'Risk Management',
                'recipient_type': 'Client',
                'template_name': 'Risk Alert - High Priority',
                'sender': 'risk.alerts@company.com',
                'subject': 'URGENT: Risk Threshold Exceeded for @@ClientName',
                'body': '''Dear @@UserName,

This is to inform you that @@ClientName has exceeded the risk threshold of @@RiskLimit.

Current Risk Level: @@CurrentRisk
Threshold: @@RiskLimit
Date/Time: @@AlertDateTime

Please review the attached risk report and take appropriate action.

Best regards,
Risk Management Team''',
                'auto_send': False,
                'data_as_attachment': True,
                'created_by': 'john.smith@company.com'
            },
            {
                'application_name': 'RDB',
                'ssg_team': 'Compliance',
                'recipient_type': 'Internal',
                'template_name': 'Daily Risk Report',
                'sender': 'compliance@company.com',
                'subject': 'Daily Risk Report - @@ReportDate',
                'body': '''Risk Management Team,

Please find the daily risk report for @@ReportDate.

Summary:
- Total Positions: @@TotalPositions
- High Risk Clients: @@HighRiskCount
- Alerts Generated: @@AlertCount

The detailed report is attached.

Compliance Team''',
                'auto_send': True,
                'data_as_attachment': True,
                'created_by': 'compliance.team@company.com'
            },
            {
                'application_name': 'RISKTECH',
                'ssg_team': 'Technology',
                'recipient_type': 'Client',
                'template_name': 'System Maintenance Notification',
                'sender': 'tech.support@company.com',
                'subject': 'Scheduled Maintenance - @@SystemName on @@MaintenanceDate',
                'body': '''Dear @@ClientName,

We will be performing scheduled maintenance on @@SystemName.

Maintenance Window:
Start: @@StartTime
End: @@EndTime
Expected Downtime: @@Duration

During this period, @@SystemName will be unavailable.

We apologize for any inconvenience.

Technical Support Team''',
                'auto_send': False,
                'data_as_attachment': False,
                'created_by': 'tech.admin@company.com'
            },
            {
                'application_name': 'RISKTECH',
                'ssg_team': 'Operations',
                'recipient_type': 'Internal',
                'template_name': 'Trade Settlement Failure',
                'sender': 'operations@company.com',
                'subject': 'Settlement Failure Alert - Trade @@TradeID',
                'body': '''Operations Team,

A trade settlement failure has occurred:

Trade Details:
- Trade ID: @@TradeID
- Client: @@ClientName
- Amount: @@TradeAmount
- Settlement Date: @@SettlementDate
- Failure Reason: @@FailureReason

Please investigate and resolve immediately.

Operations Team''',
                'auto_send': True,
                'data_as_attachment': False,
                'created_by': 'ops.manager@company.com'
            },
            {
                'application_name': 'OTHER',
                'ssg_team': 'HR',
                'recipient_type': 'Employee',
                'template_name': 'Welcome New Employee',
                'sender': 'hr@company.com',
                'subject': 'Welcome to the Team, @@EmployeeName!',
                'body': '''Dear @@EmployeeName,

Welcome to @@CompanyName! We are excited to have you join our @@Department team.

Your first day details:
- Start Date: @@StartDate
- Location: @@OfficeLocation
- Reporting Manager: @@ManagerName
- IT Setup Time: @@ITSetupTime

Please arrive 30 minutes early for your IT setup and orientation.

We look forward to working with you!

HR Team''',
                'auto_send': False,
                'data_as_attachment': False,
                'created_by': 'hr.admin@company.com'
            }
        ]
        
        # Add test templates to database
        for template_data in test_templates:
            template = Template(**template_data)
            db.session.add(template)
        
        db.session.commit()
        
        # Verify data was added
        total_templates = Template.query.count()
        rdb_count = Template.query.filter_by(application_name='RDB').count()
        risktech_count = Template.query.filter_by(application_name='RISKTECH').count()
        other_count = Template.query.filter_by(application_name='OTHER').count()
        
        print(f"✅ Successfully added {total_templates} test templates:")
        print(f"   - RDB: {rdb_count}")
        print(f"   - RISKTECH: {risktech_count}")  
        print(f"   - OTHER: {other_count}")
        print("\nTest data ready for UI testing!")

if __name__ == '__main__':
    add_test_templates()