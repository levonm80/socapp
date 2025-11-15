"""Tests for Zscaler log parser."""
import pytest
from datetime import datetime
from services.log_parser import ZscalerLogParser, LogParseError


class TestZscalerLogParser:
    """Tests for Zscaler log parser."""
    
    def test_should_parse_valid_log_line_when_all_fields_present(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/","Allowed","Ebay","Consumer Apps","72","14061","0","0","Productivity Loss","Shopping and Auctions","Online Shopping","None","None","0","None","None","ny-gre","Default Department","172.17.3.49","66.211.175.229","GET","403","curl/7.68.0","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.timestamp == datetime(2022, 6, 20, 12, 0, 0)
        assert result.location == "ny-gre"
        assert result.protocol == "HTTP"
        assert result.url == "example.com/"
        assert result.action == "Allowed"
        assert result.app_name == "Ebay"
        assert result.app_class == "Consumer Apps"
        assert result.throttle_req_size == 72
        assert result.throttle_resp_size == 14061
        assert result.req_size == 0
        assert result.resp_size == 0
        assert result.url_class == "Productivity Loss"
        assert result.url_supercat == "Shopping and Auctions"
        assert result.url_cat == "Online Shopping"
        assert result.dlp_dict == "None"
        assert result.dlp_eng == "None"
        assert result.dlp_hits == 0
        assert result.file_class == "None"
        assert result.file_type == "None"
        assert result.location2 == "ny-gre"
        assert result.department == "Default Department"
        assert result.client_ip == "172.17.3.49"
        assert result.server_ip == "66.211.175.229"
        assert result.http_method == "GET"
        assert result.http_status == 403
        assert result.user_agent == "curl/7.68.0"
        assert result.threat_category == "None"
        assert result.fw_filter == "FwFilter"
        assert result.fw_rule == "Firewall_1"
        assert result.policy_type == "Other"
        assert result.reason == "None"
    
    def test_should_extract_domain_from_url_when_url_provided(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTPS","https://example.com/path?query=1","Allowed","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.domain == "example.com"
    
    def test_should_extract_domain_from_http_url_when_http_protocol(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","http://malicious-site.xyz/phish","Blocked","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","403","UA","Phishing","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.domain == "malicious-site.xyz"
    
    def test_should_handle_url_without_protocol_when_protocol_missing(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/path","Allowed","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.domain == "example.com"
    
    def test_should_raise_error_when_missing_fields(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/"'  # Missing fields
        parser = ZscalerLogParser()
        
        # Act & Assert
        with pytest.raises(LogParseError):
            parser.parse_line(log_line)
    
    def test_should_raise_error_when_invalid_timestamp_format(self):
        # Arrange
        log_line = '"Invalid Date","ny-gre","HTTP","example.com/","Allowed","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act & Assert
        with pytest.raises(LogParseError) as exc_info:
            parser.parse_line(log_line)
        assert "timestamp" in str(exc_info.value).lower()
    
    def test_should_handle_quoted_commas_in_fields_when_present(self):
        # Arrange
        # Field with quoted comma: "value, with comma"
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/","Allowed","App, Name","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.app_name == "App, Name"
    
    def test_should_handle_empty_string_fields_when_present(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/","Allowed","","","0","0","0","0","","","","None","None","0","None","None","ny-gre","","172.17.3.49","66.211.175.229","GET","200","","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.app_name == ""
        assert result.app_class == ""
        assert result.department == ""
    
    def test_should_parse_numeric_fields_when_valid(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/","Allowed","App","Class","1000","5000","500","2000","Class","Super","Cat","None","None","5","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.throttle_req_size == 1000
        assert result.throttle_resp_size == 5000
        assert result.req_size == 500
        assert result.resp_size == 2000
        assert result.dlp_hits == 5
        assert result.http_status == 200
    
    def test_should_handle_large_resp_size_when_present(self):
        # Arrange - resp_size > 50MB (large download)
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","example.com/","Allowed","App","Class","0","0","0","52428800","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","200","UA","None","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.resp_size == 52428800  # 50MB in bytes
    
    def test_should_parse_blocked_action_when_blocked(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","malicious-site.xyz/","Blocked","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","403","UA","Phishing","FwFilter","Firewall_1","Other","Category Block","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.action == "Blocked"
        assert result.http_status == 403
        assert result.threat_category == "Phishing"
        assert result.reason == "Category Block"
    
    def test_should_parse_malicious_domain_when_in_malicious_list(self):
        # Arrange
        log_line = '"Mon Jun 20 12:00:00 2022","ny-gre","HTTP","phishing-login.co/","Blocked","App","Class","0","0","0","0","Class","Super","Cat","None","None","0","None","None","ny-gre","Dept","172.17.3.49","66.211.175.229","GET","403","UA","Phishing","FwFilter","Firewall_1","Other","None","NA","NA","N/A"'
        parser = ZscalerLogParser()
        
        # Act
        result = parser.parse_line(log_line)
        
        # Assert
        assert result.domain == "phishing-login.co"
        assert result.action == "Blocked"

