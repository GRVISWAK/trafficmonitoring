from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict


class LoginRequest(BaseModel):
    username: str
    password: str


class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "USD"
    card_number: str


class SearchQuery(BaseModel):
    query: str
    limit: int = 10


class APILogResponse(BaseModel):
    id: int
    timestamp: datetime
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    payload_size: int
    ip_address: str
    user_id: Optional[str]
    is_simulation: Optional[bool] = False

    class Config:
        from_attributes = True


class ResolutionSuggestion(BaseModel):
    category: str
    action: str
    detail: str
    priority: str


class MetricsSummary(BaseModel):
    error_rate: float
    avg_response_time_ms: float
    req_count: int
    repeat_rate: float
    usage_cluster: int
    failure_probability: float


class RootCauseAnalysis(BaseModel):
    root_cause: str
    confidence: float
    conditions_met: List[str]
    resolution_suggestions: List[ResolutionSuggestion]
    metrics_summary: MetricsSummary


class AnomalyResponse(BaseModel):
    id: int
    timestamp: datetime
    endpoint: str
    method: str
    risk_score: float
    priority: str
    failure_probability: float
    anomaly_score: float
    is_anomaly: bool
    usage_cluster: int
    req_count: int
    error_rate: float
    avg_response_time: float
    max_response_time: float
    payload_mean: float
    unique_endpoints: int
    repeat_rate: float
    status_entropy: float
    anomaly_type: Optional[str] = None
    severity: Optional[str] = None
    duration_seconds: Optional[float] = None
    impact_score: Optional[float] = None
    is_simulation: Optional[bool] = False
    root_cause_analysis: Optional[RootCauseAnalysis] = None

    class Config:
        from_attributes = True


class AdminQueryRequest(BaseModel):
    query: str


class AdminQueryResponse(BaseModel):
    results: list
    count: int
    query_interpretation: str
