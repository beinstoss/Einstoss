#!/usr/bin/env python3
"""
Script to add sample parameter data for testing
"""

from app import create_app, db
from app.models.parameter import Parameter

def add_sample_parameters():
    app = create_app()
    
    with app.app_context():
        # Clear existing parameter data
        Parameter.query.delete()
        db.session.commit()
        
        # Sample parameters
        parameters = [
            {
                'ParameterName': 'ClientName',
                'Description': 'Name of the client',
                'DataType': 'String',
                'DefaultValue': 'ABC Corp',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'UserName',
                'Description': 'Name of the user receiving the email',
                'DataType': 'String',
                'DefaultValue': 'John Doe',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'RiskLimit',
                'Description': 'Risk threshold limit',
                'DataType': 'Number',
                'DefaultValue': '1000000',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'CurrentRisk',
                'Description': 'Current risk level',
                'DataType': 'Number',
                'DefaultValue': '1250000',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'AlertDateTime',
                'Description': 'Date and time of the alert',
                'DataType': 'Date',
                'DefaultValue': '2024-01-15 14:30:00',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'ReportDate',
                'Description': 'Report generation date',
                'DataType': 'Date',
                'DefaultValue': '2024-01-15',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'TotalPositions',
                'Description': 'Total number of positions',
                'DataType': 'Number',
                'DefaultValue': '150',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'HighRiskCount',
                'Description': 'Number of high risk positions',
                'DataType': 'Number',
                'DefaultValue': '25',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'AlertCount',
                'Description': 'Number of alerts generated',
                'DataType': 'Number',
                'DefaultValue': '12',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'SystemName',
                'Description': 'Name of the system',
                'DataType': 'String',
                'DefaultValue': 'RiskTech Platform',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'MaintenanceDate',
                'Description': 'Scheduled maintenance date',
                'DataType': 'Date',
                'DefaultValue': '2024-01-20',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'StartTime',
                'Description': 'Maintenance start time',
                'DataType': 'String',
                'DefaultValue': '02:00 AM EST',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'EndTime',
                'Description': 'Maintenance end time',
                'DataType': 'String',
                'DefaultValue': '06:00 AM EST',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'Duration',
                'Description': 'Expected downtime duration',
                'DataType': 'String',
                'DefaultValue': '4 hours',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'TradeID',
                'Description': 'Unique trade identifier',
                'DataType': 'String',
                'DefaultValue': 'TRD-2024-001234',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'TradeAmount',
                'Description': 'Trade amount',
                'DataType': 'Number',
                'DefaultValue': '500000',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'SettlementDate',
                'Description': 'Trade settlement date',
                'DataType': 'Date',
                'DefaultValue': '2024-01-17',
                'CreatedBy': 'system'
            },
            {
                'ParameterName': 'FailureReason',
                'Description': 'Reason for settlement failure',
                'DataType': 'String',
                'DefaultValue': 'Insufficient funds',
                'CreatedBy': 'system'
            }
        ]
        
        # Add parameters to database
        for param_data in parameters:
            parameter = Parameter(**param_data)
            db.session.add(parameter)
        
        db.session.commit()
        
        total_params = Parameter.query.count()
        print(f"✅ Successfully added {total_params} sample parameters")
        print("\nSample parameters:")
        for param in Parameter.query.order_by(Parameter.ParameterName).all():
            print(f"   - @@{param.ParameterName} ({param.DataType}): {param.Description}")

if __name__ == '__main__':
    add_sample_parameters()