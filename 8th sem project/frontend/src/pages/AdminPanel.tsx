import React, { useState } from 'react';
import { apiService } from '../services/api';
import { AdminQueryResponse } from '../types';
import toast from 'react-hot-toast';

const AdminPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AdminQueryResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const exampleQueries = [
    'Show high risk APIs in last 10 minutes',
    'Find anomalies in /payment endpoint',
    'Show all bot-like behavior',
    'Show recent anomalies',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setLoading(true);
    
    try {
      const data = await apiService.submitAdminQuery(query);
      setResponse(data);
      
      if (data.count === 0) {
        toast('No results found', { icon: 'ℹ️' });
      } else {
        toast.success(`Found ${data.count} results`);
      }
    } catch (error) {
      console.error('Error executing query:', error);
      toast.error('Failed to execute query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-dark-text">Admin Query Panel</h1>
        <p className="text-dark-muted mt-1">Natural language queries for system analysis</p>
      </div>

      <div className="bg-dark-card rounded-lg border border-dark-border p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-dark-muted mb-2">
              Enter your query
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Show high risk APIs in last 10 minutes"
              className="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-dark-text placeholder-dark-muted focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[100px]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Execute Query'}
          </button>
        </form>

        <div className="mt-6">
          <p className="text-sm font-medium text-dark-muted mb-3">Example queries:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-dark-text hover:border-primary-500 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {response && (
        <div className="bg-dark-card rounded-lg border border-dark-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-dark-text">Query Results</h2>
            <span className="px-3 py-1 bg-primary-500/20 text-primary-500 rounded-full text-sm font-semibold">
              {response.count} results
            </span>
          </div>

          <div className="mb-4 p-4 bg-dark-bg border border-dark-border rounded-lg">
            <p className="text-sm text-dark-muted mb-1">Interpretation:</p>
            <p className="text-dark-text">{response.query_interpretation}</p>
          </div>

          {response.results.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-border">
                    {Object.keys(response.results[0]).map((key) => (
                      <th key={key} className="text-left py-3 px-4 text-sm font-semibold text-dark-muted capitalize">
                        {key.replace('_', ' ')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {response.results.map((result, index) => (
                    <tr key={index} className="border-b border-dark-border/50 hover:bg-dark-border/30 transition-colors">
                      {Object.entries(result).map(([key, value]) => (
                        <td key={key} className="py-3 px-4 text-sm text-dark-text">
                          {typeof value === 'number' 
                            ? value.toFixed(3)
                            : value?.toString() || 'N/A'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-dark-muted">
              No results found for this query
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
