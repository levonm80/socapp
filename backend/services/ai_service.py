"""AI service for OpenAI integration."""
import os
from typing import Dict, Any
from models import LogEntry, LogFile
from extensions import db


class AIService:
    """Service for AI/LLM integration."""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        # In production, use OpenAI client
        # self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_log_summary(self, log_file_id) -> Dict[str, Any]:
        """Generate SOC-style summary for log file."""
        log_file = LogFile.query.get(log_file_id)
        if not log_file:
            raise ValueError("Log file not found")
        
        # Get statistics
        entries = LogEntry.query.filter_by(log_file_id=log_file_id).all()
        total_requests = len(entries)
        blocked_events = sum(1 for e in entries if e.action == 'Blocked')
        malicious_urls = sum(1 for e in entries if e.is_anomalous)
        
        # Generate summary (simplified - would call OpenAI in production)
        summary_text = f"""
        Security Summary for {log_file.filename}
        
        Total requests analyzed: {total_requests}
        Blocked events: {blocked_events}
        Malicious URLs detected: {malicious_urls}
        
        Key findings:
        - {blocked_events} requests were blocked by the firewall
        - {malicious_urls} anomalous activities detected
        - Review high-risk users and investigate blocked requests
        
        Recommendations:
        - Investigate blocked requests for potential threats
        - Review user behavior patterns
        - Monitor anomalous activities
        """
        
        return {
            'summary': summary_text.strip(),
            'recommendations': [
                'Investigate blocked requests',
                'Review user behavior patterns',
                'Monitor anomalous activities'
            ],
            'generated_at': log_file.uploaded_at.isoformat() if log_file.uploaded_at else None
        }
    
    def explain_log_entry(self, entry: LogEntry) -> Dict[str, Any]:
        """Explain a log entry in plain English."""
        explanation = f"""
        This log entry shows a {entry.action.lower()} request from {entry.client_ip} to {entry.domain}.
        
        The request was made using {entry.user_agent} and resulted in HTTP status {entry.http_status}.
        """
        
        if entry.is_anomalous:
            explanation += f"\n\n⚠️ This entry is flagged as anomalous: {entry.anomaly_reason}"
            risk = "HIGH" if entry.anomaly_confidence and entry.anomaly_confidence > 0.8 else "MEDIUM"
            explanation += f"\nRisk level: {risk}"
            recommended_action = "Immediately investigate this entry and review user activity."
        else:
            recommended_action = "No action required. This appears to be normal traffic."
        
        return {
            'explanation': explanation.strip(),
            'risk_assessment': 'HIGH' if entry.is_anomalous else 'LOW',
            'recommended_action': recommended_action
        }
    
    def investigate(self, log_file_id, question: str) -> Dict[str, Any]:
        """Answer investigation questions using AI."""
        # Simple pattern matching (would use OpenAI in production)
        question_lower = question.lower()
        
        entries = LogEntry.query.filter_by(log_file_id=log_file_id).all()
        
        if 'phishing' in question_lower or 'malicious' in question_lower:
            relevant = [e for e in entries if e.is_anomalous and 'malicious' in str(e.anomaly_type).lower()]
            answer = f"Found {len(relevant)} malicious/phishing entries. Review the anomalous entries for details."
        elif 'blocked' in question_lower:
            relevant = [e for e in entries if e.action == 'Blocked']
            answer = f"Found {len(relevant)} blocked requests. These were blocked by the firewall policy."
        elif 'user' in question_lower:
            # Extract user from question if possible
            relevant = entries[:10]  # Simplified
            answer = f"Found user activity. Review the log entries for user behavior patterns."
        else:
            answer = "Based on the log data, I recommend reviewing the dashboard statistics and investigating any anomalous entries."
            relevant = entries[:5]
        
        return {
            'answer': answer,
            'supporting_entries': [e.to_dict() for e in relevant[:5]],
            'query_used': 'pattern_matching'  # Would be actual query in production
        }

