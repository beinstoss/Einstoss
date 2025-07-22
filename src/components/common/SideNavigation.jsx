import React, { useState } from 'react';

const SideNavigation = ({ activeRoute, onRouteChange, onCollapseChange }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navigationItems = [
    {
      id: 'templates',
      label: 'Templates',
      description: 'Manage email templates'
    },
    {
      id: 'parameters',
      label: 'Parameters',
      description: 'Configure parameters'
    },
    {
      id: 'applications',
      label: 'Applications',
      description: 'View applications'
    },
    {
      id: 'form-fields',
      label: 'Form Fields',
      description: 'Manage form fields'
    },
    {
      id: 'query',
      label: 'Query',
      description: 'Execute queries'
    }
  ];

  return (
    <div className={`bg-white shadow-lg transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'} h-screen flex flex-col fixed left-0 top-0 z-10`}>
      {/* Header */}
      <div className="px-6 py-3 border-b border-gray-200 flex items-center justify-center">
        <button
          onClick={() => {
            const newCollapsed = !isCollapsed;
            setIsCollapsed(newCollapsed);
            onCollapseChange?.(newCollapsed);
          }}
          className="p-2 rounded-md hover:bg-gray-100 transition-colors"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto">
        {navigationItems.map((item) => (
          <button
            key={item.id}
            onClick={() => !isCollapsed && onRouteChange(item.id)}
            disabled={isCollapsed}
            className={`w-full flex items-center px-4 py-3 text-left transition-colors ${
              isCollapsed 
                ? 'cursor-default'
                : activeRoute === item.id
                ? 'bg-blue-50 border-r-4 border-blue-500 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
            title={isCollapsed ? item.label : ''}
          >
            {!isCollapsed && (
              <div>
                <div className="font-medium">{item.label}</div>
                <div className="text-sm text-gray-500">{item.description}</div>
              </div>
            )}
          </button>
        ))}
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-500 text-center">
            EmailDrafter v1.0.0
          </div>
        </div>
      )}
    </div>
  );
};

export default SideNavigation;