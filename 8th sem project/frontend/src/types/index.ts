export interface APILog {
  id: number;
  timestamp: string;
  endpoint: string;
  method: string;
  response_time_ms: number;
  status_code: number;
  payload_size: number;
  ip_address: string;
  user_id: string | null;
}

export interface ResolutionSuggestion {
  category: string;
  action: string;
  detail: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface RootCauseAnalysis {
  root_cause: string;
  confidence: number;
  conditions_met: string[];
  resolution_suggestions: ResolutionSuggestion[];
  metrics_summary: {
    error_rate: number;
    avg_response_time_ms: number;
    req_count: number;
    repeat_rate: number;
    usage_cluster: number;
    failure_probability: number;
  };
}

export interface Anomaly {
  id: number;
  timestamp: string;
  endpoint: string;
  method: string;
  risk_score: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  failure_probability: number;
  anomaly_score: number;
  is_anomaly: boolean;
  usage_cluster: number;
  req_count: number;
  error_rate: number;
  avg_response_time: number;
  max_response_time: number;
  payload_mean: number;
  unique_endpoints: number;
  repeat_rate: number;
  status_entropy: number;
  anomaly_type?: string;
  severity?: string;
  duration_seconds?: number;
  impact_score?: number;
  root_cause_analysis?: RootCauseAnalysis;
}

export interface SystemStats {
  total_requests: number;
  total_anomalies: number;
  avg_response_time: number;
  error_rate: number;
  endpoint_counts?: {
    '/login': number;
    '/signup': number;
    '/search': number;
    '/profile': number;
    '/payment': number;
    '/logout': number;
  };
  live_stats: {
    mode: string;
    total_requests: number;
    current_window_count: number;
    windows_processed: number;
    window_size: number;
    is_window_full: boolean;
    last_inference: number;
    status?: string;
  };
  simulation_stats: {
    active: boolean;
    total_requests: number;
    windows_processed: number;
    anomalies_detected: number;
  };
}

export interface EndpointAnalytics {
  endpoint: string;
  total_requests: number;
  error_rate: number;
  avg_latency: number;
  failure_probability: number;
}

export interface AdminQueryResponse {
  results: any[];
  count: number;
  query_interpretation: string;
}

export interface WebSocketMessage {
  type: 'anomaly' | 'pong';
  data?: Anomaly;
}
