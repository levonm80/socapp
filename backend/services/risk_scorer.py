"""User risk score calculation service."""
from typing import Dict, List
from models import LogEntry


def calculate_user_risk_scores(log_file_id: str, entries: List[LogEntry]) -> Dict[str, Dict]:
    """
    Calculate risk scores for users based on log entries.
    
    Args:
        log_file_id: ID of the log file
        entries: List of log entries
        
    Returns:
        Dictionary mapping user_identifier to risk score data
    """
    user_stats = {}
    
    for entry in entries:
        # Use department or client_ip as user identifier
        user_id = entry.department or str(entry.client_ip)
        
        if user_id not in user_stats:
            user_stats[user_id] = {
                'anomaly_count': 0,
                'blocked_count': 0,
                'malicious_domain_count': 0,
                'total_requests': 0,
                'by_anomaly_type': {}
            }
        
        stats = user_stats[user_id]
        stats['total_requests'] += 1
        
        if entry.is_anomalous:
            stats['anomaly_count'] += 1
            anomaly_type = entry.anomaly_type or 'unknown'
            stats['by_anomaly_type'][anomaly_type] = stats['by_anomaly_type'].get(anomaly_type, 0) + 1
        
        if entry.action == 'Blocked':
            stats['blocked_count'] += 1
        
        if entry.anomaly_type == 'malicious_domain':
            stats['malicious_domain_count'] += 1
    
    # Calculate risk scores (0-100)
    risk_scores = {}
    for user_id, stats in user_stats.items():
        # Base score from anomalies
        anomaly_score = min(stats['anomaly_count'] * 10, 50)
        
        # Blocked requests score
        blocked_score = min(stats['blocked_count'] * 5, 30)
        
        # Malicious domain score
        malicious_score = min(stats['malicious_domain_count'] * 20, 40)
        
        # Total risk score (capped at 100)
        risk_score = min(anomaly_score + blocked_score + malicious_score, 100)
        
        risk_scores[user_id] = {
            'user_identifier': user_id,
            'risk_score': risk_score,
            'anomaly_count': stats['anomaly_count'],
            'blocked_count': stats['blocked_count'],
            'malicious_domain_count': stats['malicious_domain_count'],
            'metadata': stats['by_anomaly_type']
        }
    
    return risk_scores

