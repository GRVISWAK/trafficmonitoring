import axios from 'axios';
import { SystemStats, Anomaly, APILog, EndpointAnalytics, AdminQueryResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Live Mode APIs
  getStats: async (): Promise<SystemStats> => {
    const response = await api.get('/api/dashboard');
    return response.data;
  },

  getAnomalies: async (limit: number = 100): Promise<Anomaly[]> => {
    const response = await api.get(`/api/anomalies?limit=${limit}`);
    return response.data;
  },

  getLogs: async (limit: number = 100): Promise<APILog[]> => {
    const response = await api.get(`/api/logs?limit=${limit}`);
    return response.data;
  },

  // Simulation Mode APIs
  getSimulationStats: async (): Promise<any> => {
    const response = await api.get('/simulation/stats');
    return response.data;
  },

  getSimulationAnomalies: async (limit: number = 200): Promise<Anomaly[]> => {
    const response = await api.get(`/simulation/anomaly-history?limit=${limit}`);
    return response.data;
  },

  startSimulation: async (endpoint: string, duration: number = 60): Promise<any> => {
    const response = await api.post(`/simulation/start?simulated_endpoint=${endpoint}&duration_seconds=${duration}&requests_per_window=100`);
    return response.data;
  },

  clearSimulationData: async (): Promise<any> => {
    const response = await api.post('/simulation/clear-data');
    return response.data;
  },

  triggerDetection: async (): Promise<any> => {
    const response = await api.post('/api/trigger-detection');
    return response.data;
  },

  stopSimulation: async (): Promise<any> => {
    const response = await api.post('/simulation/stop');
    return response.data;
  },

  // Enhanced Simulation APIs
  startEnhancedSimulation: async (duration: number = 60, targetRps: number = 200): Promise<any> => {
    const response = await api.post(`/api/simulation/start-enhanced?duration_seconds=${duration}&target_rps=${targetRps}`);
    return response.data;
  },

  stopEnhancedSimulation: async (): Promise<any> => {
    const response = await api.post('/api/simulation/stop-enhanced');
    return response.data;
  },

  getEnhancedSimulationStats: async (): Promise<any> => {
    const response = await api.get('/api/simulation/stats-enhanced');
    return response.data;
  },

  // Visualization Graph APIs
  getRiskScoreTimeline: async (hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/risk-score-timeline?hours=${hours}`);
    return response.data;
  },

  getAnomaliesByEndpoint: async (hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/anomalies-by-endpoint?hours=${hours}`);
    return response.data;
  },

  getAnomalyTypeDistribution: async (hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/anomaly-type-distribution?hours=${hours}`);
    return response.data;
  },

  getSeverityDistribution: async (hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/severity-distribution?hours=${hours}`);
    return response.data;
  },

  getTopAffectedEndpoints: async (limit: number = 10, hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/top-affected-endpoints?limit=${limit}&hours=${hours}`);
    return response.data;
  },

  getResolutionSuggestions: async (hours: number = 24, endpoint?: string): Promise<any> => {
    const url = endpoint 
      ? `/api/graphs/resolution-suggestions?hours=${hours}&endpoint=${encodeURIComponent(endpoint)}`
      : `/api/graphs/resolution-suggestions?hours=${hours}`;
    const response = await api.get(url);
    return response.data;
  },

  getTrafficOverview: async (hours: number = 24): Promise<any> => {
    const response = await api.get(`/api/graphs/traffic-overview?hours=${hours}`);
    return response.data;
  },

  // Other APIs
  getEndpointAnalytics: async (endpoint: string): Promise<EndpointAnalytics> => {
    const encodedEndpoint = encodeURIComponent(endpoint.replace('/', ''));
    const response = await api.get(`/api/analytics/endpoint/${encodedEndpoint}`);
    return response.data;
  },

  submitAdminQuery: async (query: string): Promise<AdminQueryResponse> => {
    const response = await api.post('/api/admin/query', { query });
    return response.data;
  },
};
