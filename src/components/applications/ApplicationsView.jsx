import React, { useState } from 'react';
import axios from 'axios';

const ApplicationsView = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loaded, setLoaded] = useState(false);

  const handleLoadApplications = async () => {
    if (loading) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/applications');
      setApplications(response.data.applications || []);
      setLoaded(true);
    } catch (err) {
      setError('Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading applications...</div>;
  if (error) return (
    <div className="p-6">
      <div className="text-red-600 mb-4">{error}</div>
      <button 
        onClick={handleLoadApplications}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Retry
      </button>
    </div>
  );

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Applications</h2>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          {!loaded ? (
            <div className="text-center">
              <button 
                onClick={handleLoadApplications}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Load Applications
              </button>
            </div>
          ) : applications.length === 0 ? (
            <p className="text-gray-500">No applications found</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {applications.map((app, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">{app.displayName || app.name}</h3>
                  <p className="text-sm text-gray-600">Application: {app.name}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationsView;