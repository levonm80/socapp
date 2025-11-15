"""Anomaly detection service for log entries."""
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
from services.log_parser import ParsedLogEntry


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    is_anomalous: bool
    anomaly_type: Optional[str] = None  # burst_blocked, malicious_domain, risky_category, unusual_ua, large_download
    reason: Optional[str] = None
    confidence: Optional[float] = None  # 0-1


class AnomalyDetector:
    """Detects anomalies in log entries."""
    
    # Malicious domains list
    MALICIOUS_DOMAINS = {
        'phishing-login.co',
        'suspicious-domain.xyz',
        'malicious-example.ru'
    }
    
    # Risky URL categories
    RISKY_CATEGORIES = {
        'Proxy Avoidance',
        'Malware',
        'Phishing',
        'File Sharing'
    }
    
    # Unusual user agent patterns
    UNUSUAL_UA_PATTERNS = ['curl/', 'python-requests/']
    
    # Large download threshold (50 MB in bytes)
    LARGE_DOWNLOAD_THRESHOLD = 50_000_000
    
    # Burst detection parameters
    BURST_WINDOW_MINUTES = 5
    BURST_THRESHOLD = 10
    
    def detect_anomalies(
        self, 
        entry: ParsedLogEntry, 
        recent_entries: List[ParsedLogEntry]
    ) -> AnomalyResult:
        """
        Detect anomalies in a log entry.
        
        Args:
            entry: Current log entry to check
            recent_entries: Recent entries from same IP/user for burst detection
            
        Returns:
            AnomalyResult with detection results
        """
        anomalies = []
        
        # Check malicious domain
        if entry.domain in self.MALICIOUS_DOMAINS:
            anomalies.append(AnomalyResult(
                is_anomalous=True,
                anomaly_type='malicious_domain',
                reason=f"Domain {entry.domain} is in malicious domains list",
                confidence=0.95
            ))
        
        # Check risky category
        if entry.url_cat in self.RISKY_CATEGORIES:
            anomalies.append(AnomalyResult(
                is_anomalous=True,
                anomaly_type='risky_category',
                reason=f"URL category '{entry.url_cat}' is considered risky",
                confidence=0.7
            ))
        
        # Check unusual user agent
        if any(pattern in entry.user_agent for pattern in self.UNUSUAL_UA_PATTERNS):
            pattern = next(p for p in self.UNUSUAL_UA_PATTERNS if p in entry.user_agent)
            anomalies.append(AnomalyResult(
                is_anomalous=True,
                anomaly_type='unusual_ua',
                reason=f"Unusual user agent detected: {pattern}",
                confidence=0.6
            ))
        
        # Check large download
        if entry.resp_size > self.LARGE_DOWNLOAD_THRESHOLD:
            size_mb = entry.resp_size / (1024 * 1024)
            anomalies.append(AnomalyResult(
                is_anomalous=True,
                anomaly_type='large_download',
                reason=f"Large download detected: {size_mb:.2f} MB",
                confidence=0.65
            ))
        
        # Check burst of blocked requests
        burst_result = self._detect_burst_blocked(entry, recent_entries)
        if burst_result.is_anomalous:
            anomalies.append(burst_result)
        
        # Return highest confidence anomaly, or no anomaly
        if not anomalies:
            return AnomalyResult(is_anomalous=False)
        
        # Sort by confidence (descending) and return highest
        anomalies.sort(key=lambda x: x.confidence, reverse=True)
        return anomalies[0]
    
    def _detect_burst_blocked(
        self,
        entry: ParsedLogEntry,
        recent_entries: List[ParsedLogEntry]
    ) -> AnomalyResult:
        """
        Detect burst of blocked requests from same IP/user.
        
        Args:
            entry: Current entry
            recent_entries: Recent entries to check
            
        Returns:
            AnomalyResult for burst detection
        """
        if entry.action != "Blocked":
            return AnomalyResult(is_anomalous=False)
        
        # Filter recent entries within time window
        window_start = entry.timestamp - timedelta(minutes=self.BURST_WINDOW_MINUTES)
        recent_blocked = [
            e for e in recent_entries
            if e.timestamp >= window_start
            and e.action == "Blocked"
            and (e.client_ip == entry.client_ip or e.department == entry.department)
        ]
        
        # Count current entry + recent blocked entries
        total_blocked = len(recent_blocked) + 1
        
        if total_blocked >= self.BURST_THRESHOLD:
            return AnomalyResult(
                is_anomalous=True,
                anomaly_type='burst_blocked',
                reason=f"Burst of {total_blocked} blocked requests from {entry.client_ip} in {self.BURST_WINDOW_MINUTES}-minute window",
                confidence=0.8
            )
        
        return AnomalyResult(is_anomalous=False)

