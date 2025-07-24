import React from 'react';

const FormFieldsView = () => {
  const formFields = [
    { name: 'ApplicationName', type: 'text', label: 'Application Name', required: true },
    { name: 'SsgTeam', type: 'text', label: 'SSG Team', required: true },
    { name: 'RecipientType', type: 'select', label: 'Recipient Type', required: true },
    { name: 'TemplateName', type: 'text', label: 'Template Name', required: true },
    { name: 'Sender', type: 'email', label: 'Sender', required: true },
    { name: 'Subject', type: 'text', label: 'Subject', required: true },
    { name: 'Body', type: 'textarea', label: 'Body', required: true },
    { name: 'AutoSend', type: 'boolean', label: 'Auto Send', required: false },
    { name: 'DataAsAttachment', type: 'boolean', label: 'Data as Attachment', required: false },
  ];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Form Fields</h2>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="space-y-4">
            {formFields.map((field, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{field.label}</h3>
                    <p className="text-sm text-gray-600">
                      Field: {field.name} | Type: {field.type}
                      {field.required && (
                        <span className="ml-2 text-red-500">*Required</span>
                      )}
                    </p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {field.type}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormFieldsView;