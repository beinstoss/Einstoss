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
                'parameter_name': 'ClientName',
                'description': 'Name of the client',
                'data_type': 'String',
                'default_value': 'ABC Corp',
                'created_by': 'system'
            },
            {
                'parameter_name': 'UserName',
                'description': 'Name of the user receiving the email',
                'data_type': 'String',
                'default_value': 'John Doe',
                'created_by': 'system'
            },
            {
                'parameter_name': 'RiskLimit',
                'description': 'Risk threshold limit',
                'data_type': 'Number',
                'default_value': '1000000',
                'created_by': 'system'
            },
            {
                'parameter_name': 'CurrentRisk',
                'description': 'Current risk level',
                'data_type': 'Number',
                'default_value': '1250000',
                'created_by': 'system'
            },
            {
                'parameter_name': 'AlertDateTime',
                'description': 'Date and time of the alert',
                'data_type': 'Date',
                'default_value': '2024-01-15 14:30:00',
                'created_by': 'system'
            },
            {
                'parameter_name': 'ReportDate',
                'description': 'Report generation date',
                'data_type': 'Date',
                'default_value': '2024-01-15',
                'created_by': 'system'
            },
            {
                'parameter_name': 'TotalPositions',
                'description': 'Total number of positions',
                'data_type': 'Number',
                'default_value': '150',
                'created_by': 'system'
            },
            {
                'parameter_name': 'HighRiskCount',
                'description': 'Number of high risk positions',
                'data_type': 'Number',
                'default_value': '25',
                'created_by': 'system'
            },
            {
                'parameter_name': 'AlertCount',
                'description': 'Number of alerts generated',
                'data_type': 'Number',
                'default_value': '12',
                'created_by': 'system'
            },
            {
                'parameter_name': 'SystemName',
                'description': 'Name of the system',
                'data_type': 'String',
                'default_value': 'RiskTech Platform',
                'created_by': 'system'
            },
            {
                'parameter_name': 'MaintenanceDate',
                'description': 'Scheduled maintenance date',
                'data_type': 'Date',
                'default_value': '2024-01-20',
                'created_by': 'system'
            },
            {
                'parameter_name': 'StartTime',
                'description': 'Maintenance start time',
                'data_type': 'String',
                'default_value': '02:00 AM EST',
                'created_by': 'system'
            },
            {
                'parameter_name': 'EndTime',
                'description': 'Maintenance end time',
                'data_type': 'String',
                'default_value': '06:00 AM EST',
                'created_by': 'system'
            },
            {
                'parameter_name': 'Duration',
                'description': 'Expected downtime duration',
                'data_type': 'String',
                'default_value': '4 hours',
                'created_by': 'system'
            },
            {
                'parameter_name': 'TradeID',
                'description': 'Unique trade identifier',
                'data_type': 'String',
                'default_value': 'TRD-2024-001234',
                'created_by': 'system'
            },
            {
                'parameter_name': 'TradeAmount',
                'description': 'Trade amount',
                'data_type': 'Number',
                'default_value': '500000',
                'created_by': 'system'
            },
            {
                'parameter_name': 'SettlementDate',
                'description': 'Trade settlement date',
                'data_type': 'Date',
                'default_value': '2024-01-17',
                'created_by': 'system'
            },
            {
                'parameter_name': 'FailureReason',
                'description': 'Reason for settlement failure',
                'data_type': 'String',
                'default_value': 'Insufficient funds',
                'created_by': 'system'
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
        for param in Parameter.query.order_by(Parameter.parameter_name).all():
            print(f"   - @@{param.parameter_name} ({param.data_type}): {param.description}")

if __name__ == '__main__':
    add_sample_parameters()