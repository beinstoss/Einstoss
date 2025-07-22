import React from 'react';

const ApplicationSelector = ({ selectedApplication, onApplicationChange, sidebarCollapsed }) => {
  return (
    <div className={`bg-white shadow-sm border-r border-gray-200 w-64 h-screen fixed top-0 z-10 transition-all duration-300 ${sidebarCollapsed ? 'left-16' : 'left-64'}`}>
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Filter by Application</h3>
        <div className="space-y-2">
          <label htmlFor="application" className="block text-xs font-medium text-gray-700">
            Select Application:
          </label>
          <select
            id="application"
            value={selectedApplication}
            onChange={(e) => onApplicationChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="RDB">RDB</option>
            <option value="RISKTECH">RISKTECH</option>
            <option value="OTHER">OTHER</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default ApplicationSelector;