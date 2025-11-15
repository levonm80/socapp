"""Tests for anomaly detector."""
import pytest
from datetime import datetime, timedelta
from services.anomaly_detector import AnomalyDetector, AnomalyResult
from services.log_parser import ParsedLogEntry


class TestAnomalyDetector:
    """Tests for AnomalyDetector."""
    
    def test_should_detect_malicious_domain_when_domain_in_list(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="phishing-login.co/path",
            domain="phishing-login.co",
            action="Blocked",
            app_name="Unknown",
            app_class="Consumer Apps",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Security Risk",
            url_supercat="Malicious",
            url_cat="Phishing",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=403,
            user_agent="Mozilla/5.0",
            threat_category="Phishing",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "malicious_domain"
        assert "phishing-login.co" in result.reason.lower()
        assert result.confidence == 0.95
    
    def test_should_detect_risky_category_when_category_in_risky_list(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="example.com/",
            domain="example.com",
            action="Allowed",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Security Risk",
            url_supercat="Malicious",
            url_cat="Malware",  # Risky category
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=200,
            user_agent="Mozilla/5.0",
            threat_category="None",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "risky_category"
        assert "malware" in result.reason.lower()
        assert result.confidence == 0.7
    
    def test_should_detect_unusual_user_agent_when_curl_detected(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="example.com/",
            domain="example.com",
            action="Allowed",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Business Use",
            url_supercat="Business",
            url_cat="Business",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=200,
            user_agent="curl/7.68.0",  # Unusual UA
            threat_category="None",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "unusual_ua"
        assert "curl" in result.reason.lower()
        assert result.confidence == 0.6
    
    def test_should_detect_unusual_user_agent_when_python_requests_detected(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="example.com/",
            domain="example.com",
            action="Allowed",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Business Use",
            url_supercat="Business",
            url_cat="Business",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=200,
            user_agent="python-requests/2.28.1",  # Unusual UA
            threat_category="None",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "unusual_ua"
        assert "python-requests" in result.reason.lower()
        assert result.confidence == 0.6
    
    def test_should_detect_large_download_when_resp_size_exceeds_threshold(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="example.com/download",
            domain="example.com",
            action="Allowed",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=52428801,  # > 50MB
            url_class="Business Use",
            url_supercat="Business",
            url_cat="Business",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=200,
            user_agent="Mozilla/5.0",
            threat_category="None",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "large_download"
        assert "50" in result.reason or "large" in result.reason.lower()
        assert result.confidence == 0.65
    
    def test_should_detect_burst_blocked_when_multiple_blocked_in_window(self):
        # Arrange
        detector = AnomalyDetector()
        base_time = datetime(2022, 6, 20, 12, 0, 0)
        
        # Create 10 blocked entries from same IP in 5-minute window
        recent_entries = []
        for i in range(10):
            entry = ParsedLogEntry(
                timestamp=base_time - timedelta(minutes=4-i),
                location="ny-gre",
                protocol="HTTP",
                url="example.com/",
                domain="example.com",
                action="Blocked",
                app_name="App",
                app_class="Class",
                throttle_req_size=0,
                throttle_resp_size=0,
                req_size=0,
                resp_size=0,
                url_class="Security Risk",
                url_supercat="Malicious",
                url_cat="Phishing",
                dlp_dict="None",
                dlp_eng="None",
                dlp_hits=0,
                file_class="None",
                file_type="None",
                location2="ny-gre",
                department="Engineering",
                client_ip="172.17.3.49",  # Same IP
                server_ip="66.211.175.229",
                http_method="GET",
                http_status=403,
                user_agent="Mozilla/5.0",
                threat_category="Phishing",
                fw_filter="FwFilter",
                fw_rule="Firewall_1",
                policy_type="Other",
                reason="Category Block"
            )
            recent_entries.append(entry)
        
        current_entry = ParsedLogEntry(
            timestamp=base_time,
            location="ny-gre",
            protocol="HTTP",
            url="example.com/",
            domain="example.com",
            action="Blocked",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Security Risk",
            url_supercat="Malicious",
            url_cat="Phishing",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",  # Same IP
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=403,
            user_agent="Mozilla/5.0",
            threat_category="Phishing",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="Category Block"
        )
        
        # Act
        result = detector.detect_anomalies(current_entry, recent_entries)
        
        # Assert
        assert result.is_anomalous is True
        assert result.anomaly_type == "burst_blocked"
        assert "burst" in result.reason.lower() or "blocked" in result.reason.lower()
        assert result.confidence == 0.8
    
    def test_should_not_detect_anomaly_when_normal_entry(self):
        # Arrange
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTPS",
            url="https://google.com/",
            domain="google.com",
            action="Allowed",
            app_name="Google",
            app_class="Search Engines",
            throttle_req_size=1000,
            throttle_resp_size=5000,
            req_size=500,
            resp_size=2000,
            url_class="Business Use",
            url_supercat="Search Engines",
            url_cat="Search Engine",
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=200,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            threat_category="None",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert
        assert result.is_anomalous is False
        assert result.anomaly_type is None
        assert result.reason is None
        assert result.confidence is None
    
    def test_should_prioritize_malicious_domain_over_other_anomalies(self):
        # Arrange - Entry that matches multiple rules (malicious domain + risky category)
        detector = AnomalyDetector()
        log_entry = ParsedLogEntry(
            timestamp=datetime(2022, 6, 20, 12, 0, 0),
            location="ny-gre",
            protocol="HTTP",
            url="phishing-login.co/",
            domain="phishing-login.co",  # Malicious domain
            action="Blocked",
            app_name="App",
            app_class="Class",
            throttle_req_size=0,
            throttle_resp_size=0,
            req_size=0,
            resp_size=0,
            url_class="Security Risk",
            url_supercat="Malicious",
            url_cat="Phishing",  # Also risky category
            dlp_dict="None",
            dlp_eng="None",
            dlp_hits=0,
            file_class="None",
            file_type="None",
            location2="ny-gre",
            department="Engineering",
            client_ip="172.17.3.49",
            server_ip="66.211.175.229",
            http_method="GET",
            http_status=403,
            user_agent="Mozilla/5.0",
            threat_category="Phishing",
            fw_filter="FwFilter",
            fw_rule="Firewall_1",
            policy_type="Other",
            reason="None"
        )
        
        # Act
        result = detector.detect_anomalies(log_entry, [])
        
        # Assert - Should detect malicious_domain (higher confidence)
        assert result.is_anomalous is True
        assert result.anomaly_type == "malicious_domain"  # Higher confidence (0.95 > 0.7)
        assert result.confidence == 0.95

