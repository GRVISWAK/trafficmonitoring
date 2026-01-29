"""
Visualization and Analytics Endpoints
Provides graph data for dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict
from database import get_db, AnomalyLog, APILog

router = APIRouter()


@router.get("/api/graphs/risk-score-timeline")
async def get_risk_score_timeline(hours: int = 24, db: Session = Depends(get_db)):
    """
    Get risk score timeline for the last N hours
    Returns time-series data of risk scores
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    anomalies = db.query(AnomalyLog).filter(
        AnomalyLog.timestamp >= start_time
    ).order_by(AnomalyLog.timestamp).all()
    
    timeline = []
    for anomaly in anomalies:
        timeline.append({
            'timestamp': anomaly.timestamp.isoformat(),
            'risk_score': anomaly.risk_score,
            'endpoint': anomaly.endpoint,
            'severity': anomaly.severity,
            'anomaly_type': anomaly.anomaly_type
        })
    
    return {
        'timeline': timeline,
        'count': len(timeline),
        'period_hours': hours
    }


@router.get("/api/graphs/anomalies-by-endpoint")
async def get_anomalies_by_endpoint(hours: int = 24, db: Session = Depends(get_db)):
    """
    Get anomaly count grouped by endpoint
    Shows which endpoints have the most anomalies
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        AnomalyLog.endpoint,
        func.count(AnomalyLog.id).label('anomaly_count'),
        func.avg(AnomalyLog.risk_score).label('avg_risk_score'),
        func.avg(AnomalyLog.impact_score).label('avg_impact_score')
    ).filter(
        AnomalyLog.timestamp >= start_time
    ).group_by(
        AnomalyLog.endpoint
    ).all()
    
    by_endpoint = []
    for result in results:
        by_endpoint.append({
            'endpoint': result.endpoint,
            'anomaly_count': result.anomaly_count,
            'avg_risk_score': round(result.avg_risk_score, 2) if result.avg_risk_score else 0,
            'avg_impact_score': round(result.avg_impact_score, 3) if result.avg_impact_score else 0
        })
    
    # Sort by anomaly count descending
    by_endpoint.sort(key=lambda x: x['anomaly_count'], reverse=True)
    
    return {
        'by_endpoint': by_endpoint,
        'count': len(by_endpoint),
        'period_hours': hours
    }


@router.get("/api/graphs/anomaly-type-distribution")
async def get_anomaly_type_distribution(hours: int = 24, db: Session = Depends(get_db)):
    """
    Get distribution of anomaly types
    Shows percentage of each anomaly type
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        AnomalyLog.anomaly_type,
        func.count(AnomalyLog.id).label('count')
    ).filter(
        AnomalyLog.timestamp >= start_time,
        AnomalyLog.anomaly_type.isnot(None)
    ).group_by(
        AnomalyLog.anomaly_type
    ).all()
    
    total = sum(r.count for r in results)
    
    distribution = []
    for result in results:
        percentage = (result.count / total * 100) if total > 0 else 0
        distribution.append({
            'anomaly_type': result.anomaly_type,
            'count': result.count,
            'percentage': round(percentage, 2)
        })
    
    # Sort by count descending
    distribution.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        'distribution': distribution,
        'total_anomalies': total,
        'period_hours': hours
    }


@router.get("/api/graphs/severity-distribution")
async def get_severity_distribution(hours: int = 24, db: Session = Depends(get_db)):
    """
    Get distribution of anomaly severities
    Shows percentage of each severity level
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        AnomalyLog.severity,
        func.count(AnomalyLog.id).label('count')
    ).filter(
        AnomalyLog.timestamp >= start_time,
        AnomalyLog.severity.isnot(None)
    ).group_by(
        AnomalyLog.severity
    ).all()
    
    total = sum(r.count for r in results)
    
    distribution = []
    severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    
    for result in results:
        percentage = (result.count / total * 100) if total > 0 else 0
        distribution.append({
            'severity': result.severity,
            'count': result.count,
            'percentage': round(percentage, 2),
            'order': severity_order.get(result.severity, 0)
        })
    
    # Sort by severity order
    distribution.sort(key=lambda x: x['order'], reverse=True)
    
    return {
        'distribution': distribution,
        'total_anomalies': total,
        'period_hours': hours
    }


@router.get("/api/graphs/top-affected-endpoints")
async def get_top_affected_endpoints(limit: int = 10, hours: int = 24, db: Session = Depends(get_db)):
    """
    Get top affected endpoints ranked by severity and impact
    Returns endpoints with highest risk scores and impact scores
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    results = db.query(
        AnomalyLog.endpoint,
        func.count(AnomalyLog.id).label('anomaly_count'),
        func.avg(AnomalyLog.risk_score).label('avg_risk_score'),
        func.max(AnomalyLog.risk_score).label('max_risk_score'),
        func.avg(AnomalyLog.impact_score).label('avg_impact_score'),
        func.max(AnomalyLog.impact_score).label('max_impact_score'),
        func.avg(AnomalyLog.failure_probability).label('avg_failure_probability')
    ).filter(
        AnomalyLog.timestamp >= start_time
    ).group_by(
        AnomalyLog.endpoint
    ).all()
    
    top_endpoints = []
    for result in results:
        # Calculate composite risk score
        composite_score = (
            (result.avg_risk_score or 0) * 0.4 +
            (result.max_risk_score or 0) * 0.3 +
            (result.avg_impact_score or 0) * 100 * 0.3
        )
        
        top_endpoints.append({
            'endpoint': result.endpoint,
            'anomaly_count': result.anomaly_count,
            'avg_risk_score': round(result.avg_risk_score, 2) if result.avg_risk_score else 0,
            'max_risk_score': round(result.max_risk_score, 2) if result.max_risk_score else 0,
            'avg_impact_score': round(result.avg_impact_score, 3) if result.avg_impact_score else 0,
            'max_impact_score': round(result.max_impact_score, 3) if result.max_impact_score else 0,
            'avg_failure_probability': round(result.avg_failure_probability, 3) if result.avg_failure_probability else 0,
            'composite_score': round(composite_score, 2)
        })
    
    # Sort by composite score descending
    top_endpoints.sort(key=lambda x: x['composite_score'], reverse=True)
    
    return {
        'top_endpoints': top_endpoints[:limit],
        'total_endpoints': len(top_endpoints),
        'period_hours': hours
    }


@router.get("/api/graphs/resolution-suggestions")
async def get_resolution_suggestions(endpoint: str = None, hours: int = 24, db: Session = Depends(get_db)):
    """
    Get resolution suggestions for anomalies
    Returns unique, actionable suggestions ranked by severity and priority
    """
    from resolution_engine import resolution_engine
    
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(AnomalyLog).filter(
        AnomalyLog.timestamp >= start_time,
        AnomalyLog.anomaly_type.isnot(None)
    )
    
    if endpoint:
        query = query.filter(AnomalyLog.endpoint == endpoint)
    
    anomalies = query.order_by(AnomalyLog.risk_score.desc()).limit(20).all()
    
    all_suggestions = []
    seen_suggestions = set()
    
    for anomaly in anomalies:
        resolutions = resolution_engine.generate_resolutions(
            anomaly.anomaly_type, 
            anomaly.severity
        )
        
        for resolution in resolutions:
            # Create unique key to avoid duplicates
            suggestion_key = f"{resolution['category']}:{resolution['action']}"
            
            if suggestion_key not in seen_suggestions:
                seen_suggestions.add(suggestion_key)
                all_suggestions.append({
                    **resolution,
                    'endpoint': anomaly.endpoint,
                    'anomaly_type': anomaly.anomaly_type,
                    'severity': anomaly.severity,
                    'impact_score': anomaly.impact_score,
                    'timestamp': anomaly.timestamp.isoformat()
                })
    
    # Rank by priority
    priority_rank = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
    all_suggestions.sort(key=lambda x: (
        priority_rank.get(x['priority'], 0),
        x.get('impact_score', 0)
    ), reverse=True)
    
    # Group by severity
    by_severity = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for suggestion in all_suggestions:
        severity = suggestion.get('severity', 'LOW')
        if severity in by_severity:
            by_severity[severity].append(suggestion)
    
    return {
        'suggestions': all_suggestions[:50],  # Limit to top 50
        'by_severity': by_severity,
        'total_unique_suggestions': len(all_suggestions),
        'period_hours': hours
    }


@router.get("/api/graphs/traffic-overview")
async def get_traffic_overview(hours: int = 24, db: Session = Depends(get_db)):
    """
    Get overall traffic overview with request counts and error rates
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get request counts per endpoint
    endpoint_stats = db.query(
        APILog.endpoint,
        func.count(APILog.id).label('request_count'),
        func.avg(APILog.response_time_ms).label('avg_response_time'),
        func.sum(func.case((APILog.status_code >= 400, 1), else_=0)).label('error_count')
    ).filter(
        APILog.timestamp >= start_time
    ).group_by(
        APILog.endpoint
    ).all()
    
    overview = []
    for stat in endpoint_stats:
        error_rate = (stat.error_count / stat.request_count) if stat.request_count > 0 else 0
        overview.append({
            'endpoint': stat.endpoint,
            'request_count': stat.request_count,
            'avg_response_time': round(stat.avg_response_time, 2) if stat.avg_response_time else 0,
            'error_count': stat.error_count,
            'error_rate': round(error_rate, 3)
        })
    
    # Sort by request count
    overview.sort(key=lambda x: x['request_count'], reverse=True)
    
    total_requests = sum(s['request_count'] for s in overview)
    total_errors = sum(s['error_count'] for s in overview)
    overall_error_rate = (total_errors / total_requests) if total_requests > 0 else 0
    
    return {
        'overview': overview,
        'total_requests': total_requests,
        'total_errors': total_errors,
        'overall_error_rate': round(overall_error_rate, 3),
        'period_hours': hours
    }
