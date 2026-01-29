import React, { useState } from 'react';
import { apiService } from '../services/api';
import { EndpointAnalytics } from '../types';
import toast from 'react-hot-toast';

const Analytics: React.FC = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState('/login');
  const [analytics, setAnalytics] = useState<EndpointAnalytics | null>(null);
  const [loading, setLoading] = useState(false);

  const endpoints = ['/login', '/payment', '/search', '/health'];

  const handleEndpointChange = async (endpoint: string) => {
    setSelectedEndpoint(endpoint);
    setLoading(true);
    
    try {
      const data = await apiService.getEndpointAnalytics(endpoint);
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Failed to load endpoint analytics');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    handleEndpointChange(selectedEndpoint);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-dark-text">API Analytics</h1>
        <p className="text-dark-muted mt-1">Detailed metrics for individual endpoints</p>
      </div>

      <div className="bg-dark-card rounded-lg border border-dark-border p-6">
        <label className="block text-sm font-medium text-dark-muted mb-2">
          Select Endpoint
        </label>
        <select
          value={selectedEndpoint}
          onChange={(e) => handleEndpointChange(e.target.value)}
          className="w-full md:w-64 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-dark-text focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {endpoints.map((endpoint) => (
            <option key={endpoint} value={endpoint}>
              {endpoint}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500" />
        </div>
      ) : analytics ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-dark-card rounded-lg border border-primary-500 p-6">
              <h3 className="text-sm font-medium text-dark-muted mb-2">Total Requests</h3>
              <p className="text-3xl font-bold text-dark-text">
                {analytics.total_requests.toLocaleString()}
              </p>
            </div>

            <div className="bg-dark-card rounded-lg border border-danger-500 p-6">
              <h3 className="text-sm font-medium text-dark-muted mb-2">Error Rate</h3>
              <p className="text-3xl font-bold text-dark-text">
                {(analytics.error_rate * 100).toFixed(2)}%
              </p>
              <div className="mt-2 w-full bg-dark-border rounded-full h-2">
                <div
                  className="bg-danger-500 h-2 rounded-full"
                  style={{ width: `${analytics.error_rate * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-dark-card rounded-lg border border-warning-500 p-6">
              <h3 className="text-sm font-medium text-dark-muted mb-2">Avg Latency</h3>
              <p className="text-3xl font-bold text-dark-text">
                {analytics.avg_latency.toFixed(0)}ms
              </p>
              <p className="text-xs text-dark-muted mt-1">
                {analytics.avg_latency < 200 ? 'Excellent' : analytics.avg_latency < 500 ? 'Good' : 'Needs attention'}
              </p>
            </div>

            <div className="bg-dark-card rounded-lg border border-warning-500 p-6">
              <h3 className="text-sm font-medium text-dark-muted mb-2">Failure Probability</h3>
              <p className="text-3xl font-bold text-dark-text">
                {(analytics.failure_probability * 100).toFixed(1)}%
              </p>
              <div className="mt-2 w-full bg-dark-border rounded-full h-2">
                <div
                  className="bg-warning-500 h-2 rounded-full"
                  style={{ width: `${analytics.failure_probability * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="bg-dark-card rounded-lg border border-dark-border p-6">
            <h2 className="text-xl font-bold mb-4 text-dark-text">Performance Insights</h2>
            
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center">
                  <span className="text-primary-500">📈</span>
                </div>
                <div>
                  <h4 className="font-semibold text-dark-text">Request Volume</h4>
                  <p className="text-sm text-dark-muted">
                    This endpoint has received {analytics.total_requests.toLocaleString()} total requests
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-danger-500/20 flex items-center justify-center">
                  <span className="text-danger-500">⚠️</span>
                </div>
                <div>
                  <h4 className="font-semibold text-dark-text">Error Analysis</h4>
                  <p className="text-sm text-dark-muted">
                    {analytics.error_rate > 0.1
                      ? `High error rate detected (${(analytics.error_rate * 100).toFixed(2)}%). Immediate attention required.`
                      : `Error rate is within acceptable limits (${(analytics.error_rate * 100).toFixed(2)}%).`}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-warning-500/20 flex items-center justify-center">
                  <span className="text-warning-500">⏱️</span>
                </div>
                <div>
                  <h4 className="font-semibold text-dark-text">Latency Performance</h4>
                  <p className="text-sm text-dark-muted">
                    Average response time is {analytics.avg_latency.toFixed(0)}ms.
                    {analytics.avg_latency < 200
                      ? ' Excellent performance!'
                      : analytics.avg_latency < 500
                      ? ' Good performance.'
                      : ' Consider optimization.'}
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-warning-500/20 flex items-center justify-center">
                  <span className="text-warning-500">🎯</span>
                </div>
                <div>
                  <h4 className="font-semibold text-dark-text">Failure Prediction</h4>
                  <p className="text-sm text-dark-muted">
                    ML models predict a {(analytics.failure_probability * 100).toFixed(1)}% probability of failure.
                    {analytics.failure_probability > 0.5
                      ? ' High risk - monitor closely!'
                      : ' Low risk - normal operation.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default Analytics;
