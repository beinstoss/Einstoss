import React, { useState, useRef } from 'react';

const TopBar = () => {
  const [user, setUser] = useState(null); // null = logged out, object = logged in
  const [showEnvDropdown, setShowEnvDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const handleSignIn = () => {
    // Simulate sign in - in real app this would integrate with auth service
    setUser({ name: 'John Doe', email: 'john.doe@company.com' });
  };

  const handleSignOut = () => {
    setUser(null);
  };

  const environments = [
    { name: 'DEV', url: '/docs/dev' },
    { name: 'INT', url: '/docs/int' },
    { name: 'PROD', url: '/docs/prod' },
    { name: 'POS-INT', url: '/docs/pos-int' },
    { name: 'POS-PROD', url: '/docs/pos-prod' }
  ];

  const handleDropdownToggle = () => {
    setShowEnvDropdown(!showEnvDropdown);
  };

  const handleDropdownClose = () => {
    setShowEnvDropdown(false);
  };

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      {/* Title Bar */}
      <div className="px-6 py-3 border-b border-gray-100">
        <h1 className="text-2xl font-bold text-gray-900">Email Drafter</h1>
      </div>

      {/* Navigation Bar */}
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* Documentation Dropdown */}
          <div className="relative">
            <button
              onClick={handleDropdownToggle}
              onBlur={(e) => {
                // Close dropdown when clicking outside, but not when clicking inside dropdown
                if (!e.relatedTarget || !e.currentTarget.parentNode.contains(e.relatedTarget)) {
                  setTimeout(() => setShowEnvDropdown(false), 150);
                }
              }}
              className="flex items-center text-sm text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              Documentation
              <svg className="ml-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>

            {showEnvDropdown && (
              <div className="absolute left-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-50">
                <div className="py-1">
                  {environments.map((env) => (
                    <a
                      key={env.name}
                      href={env.url}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                      onClick={handleDropdownClose}
                    >
                      {env.name}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* User Authentication and Version */}
        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">Welcome, {user.name}</span>
              <button
                onClick={handleSignOut}
                className="text-sm text-red-600 hover:text-red-800 focus:outline-none"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              onClick={handleSignIn}
              className="text-sm text-blue-600 hover:text-blue-800 focus:outline-none"
            >
              Sign In
            </button>
          )}
          
          {/* Version */}
          <div className="text-sm text-gray-500">
            v1.0.0
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;