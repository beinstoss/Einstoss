import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import TopBar from './components/common/TopBar';
import SideNavigation from './components/common/SideNavigation';
import TemplatesTable from './components/templates/TemplatesTable';
import ParametersView from './components/parameters/ParametersView';
import ApplicationsView from './components/applications/ApplicationsView';
import QueryView from './components/query/QueryView';
import FormFieldsView from './components/forms/FormFieldsView';

function App() {
  const [activeRoute, setActiveRoute] = useState('templates');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState('RDB');

  const renderContent = () => {
    switch (activeRoute) {
      case 'templates':
        return (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6 p-6 pb-0">Templates</h2>
            <div className="px-6 mb-4">
              <div className="flex items-center gap-3">
                <label htmlFor="application" className="text-sm font-medium text-gray-700">
                  Application:
                </label>
                <select
                  id="application"
                  value={selectedApplication}
                  onChange={(e) => setSelectedApplication(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="RDB">RDB</option>
                  <option value="RISKTECH">RISKTECH</option>
                  <option value="OTHER">OTHER</option>
                </select>
              </div>
            </div>
            <TemplatesTable selectedApplication={selectedApplication} />
          </div>
        );
      case 'parameters':
        return <ParametersView />;
      case 'applications':
        return <ApplicationsView />;
      case 'query':
        return <QueryView />;
      case 'form-fields':
        return <FormFieldsView />;
      default:
        return <div className="p-6"><h1 className="text-2xl font-bold">Templates</h1></div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <SideNavigation 
        activeRoute={activeRoute} 
        onRouteChange={setActiveRoute}
        onCollapseChange={setSidebarCollapsed}
      />
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        <TopBar />
        <div className="min-h-screen bg-gray-100">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);