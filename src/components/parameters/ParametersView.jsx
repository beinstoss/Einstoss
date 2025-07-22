import React, { useState } from 'react';

const ParametersView = () => {
  const [parameters, setParameters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loaded, setLoaded] = useState(false);

  const handleLoadParameters = async () => {
    if (loading) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/parameters');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setParameters(data.parameters || []);
      setLoaded(true);
    } catch (err) {
      setError('Failed to load parameters');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading parameters...</div>;
  if (error) return (
    <div className="p-6">
      <div className="text-red-600 mb-4">{error}</div>
      <button 
        onClick={handleLoadParameters}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Retry
      </button>
    </div>
  );

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Parameters</h2>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          {!loaded ? (
            <div className="text-center">
              <button 
                onClick={handleLoadParameters}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Load Parameters
              </button>
            </div>
          ) : parameters.length === 0 ? (
            <p className="text-gray-500">No parameters found</p>
          ) : (
            <div className="space-y-4">
              {parameters.map((param, index) => (
                <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                  <div className="font-medium text-gray-900">{param.name || param}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ParametersView;