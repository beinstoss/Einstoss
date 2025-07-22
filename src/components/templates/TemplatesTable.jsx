import React, { useState, useEffect } from 'react';

const TemplatesTable = ({ selectedApplication = 'RDB' }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/api/templates/?application=${selectedApplication}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setTemplates(data || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch templates');
        setTemplates([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, [selectedApplication]);

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="text-gray-600">Loading templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <div className="text-red-800">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">

      {templates.length === 0 ? (
        <div className="text-center p-6 text-gray-500 bg-white border border-gray-200 rounded-lg">
          No templates found for {selectedApplication}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Template Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    SSG Team
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Recipient Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sender
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subject
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created By
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {templates.map((template) => (
                  <tr key={template.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900">
                        {template.templateName}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">{template.ssgTeam}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">{template.recipientType}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">{template.sender}</div>
                    </td>
                    <td className="px-4 py-3 max-w-xs">
                      <div className="text-sm text-gray-900 truncate" title={template.subject}>
                        {template.subject}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">{template.createdBy}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm text-gray-900">
                        {new Date(template.creationTime).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex space-x-3">
                        <button className="text-sm text-blue-600 hover:text-blue-900">
                          View
                        </button>
                        <button className="text-sm text-blue-600 hover:text-blue-900">
                          Edit
                        </button>
                        <button className="text-sm text-red-600 hover:text-red-900">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplatesTable;