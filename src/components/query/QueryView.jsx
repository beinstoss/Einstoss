import React, { useState } from 'react';
import useDebounce from '../../hooks/useDebounce';

const QueryView = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const [debouncedExecute] = useDebounce(() => {
    if (query.trim()) {
      setResults(`Query executed: "${query}"`);
      setLoading(false);
    }
  }, 300);

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    debouncedExecute();
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Query</h2>
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <form onSubmit={handleQuerySubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your query
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder="Enter your query here..."
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Executing...' : 'Execute Query'}
            </button>
          </form>
          
          {results && (
            <div className="mt-6 p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-900 mb-2">Results:</h3>
              <p className="text-gray-700">{results}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QueryView;