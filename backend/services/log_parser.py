"""Zscaler NSS web proxy log parser."""
import csv
import io
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional
from dataclasses import dataclass


class LogParseError(Exception):
    """Error parsing log line."""
    pass


@dataclass
class ParsedLogEntry:
    """Parsed log entry data."""
    timestamp: datetime
    location: str
    protocol: str
    url: str
    domain: str
    action: str
    app_name: str
    app_class: str
    throttle_req_size: int
    throttle_resp_size: int
    req_size: int
    resp_size: int
    url_class: str
    url_supercat: str
    url_cat: str
    dlp_dict: str
    dlp_eng: str
    dlp_hits: int
    file_class: str
    file_type: str
    location2: str
    department: str
    client_ip: str
    server_ip: str
    http_method: str
    http_status: int
    user_agent: str
    threat_category: str
    fw_filter: str
    fw_rule: str
    policy_type: str
    reason: str


class ZscalerLogParser:
    """Parser for Zscaler NSS web proxy logs."""
    
    # Expected number of fields in Zscaler log format
    EXPECTED_FIELD_COUNT = 34
    
    def parse_line(self, line: str) -> ParsedLogEntry:
        """
        Parse a single Zscaler log line.
        
        Args:
            line: CSV line with 34 quoted fields
            
        Returns:
            ParsedLogEntry with all fields parsed
            
        Raises:
            LogParseError: If line cannot be parsed
        """
        try:
            # Use CSV reader to handle quoted fields and commas correctly
            reader = csv.reader(io.StringIO(line))
            fields = next(reader)
            
            if len(fields) != self.EXPECTED_FIELD_COUNT:
                raise LogParseError(
                    f"Expected {self.EXPECTED_FIELD_COUNT} fields, got {len(fields)}"
                )
            
            # Parse timestamp (field 0)
            timestamp = self._parse_timestamp(fields[0])
            
            # Extract domain from URL (field 3)
            url = fields[3]
            domain = self._extract_domain(url)
            
            # Parse numeric fields
            throttle_req_size = self._parse_int(fields[7], 0)
            throttle_resp_size = self._parse_int(fields[8], 0)
            req_size = self._parse_int(fields[9], 0)
            resp_size = self._parse_int(fields[10], 0)
            dlp_hits = self._parse_int(fields[16], 0)
            http_status = self._parse_int(fields[24], 0)  # Field 24, not 25
            
            return ParsedLogEntry(
                timestamp=timestamp,
                location=fields[1],
                protocol=fields[2],
                url=url,
                domain=domain,
                action=fields[4],
                app_name=fields[5],
                app_class=fields[6],
                throttle_req_size=throttle_req_size,
                throttle_resp_size=throttle_resp_size,
                req_size=req_size,
                resp_size=resp_size,
                url_class=fields[11],
                url_supercat=fields[12],
                url_cat=fields[13],
                dlp_dict=fields[14],
                dlp_eng=fields[15],
                dlp_hits=dlp_hits,
                file_class=fields[17],
                file_type=fields[18],
                location2=fields[19],
                department=fields[20],
                client_ip=fields[21],
                server_ip=fields[22],
                http_method=fields[23],
                http_status=http_status,
                user_agent=fields[25],  # Field 25, not 26
                threat_category=fields[26],  # Field 26, not 27
                fw_filter=fields[27],  # Field 27, not 28
                fw_rule=fields[28],  # Field 28, not 29
                policy_type=fields[29],  # Field 29, not 30
                reason=fields[30]  # Field 30, not 31
            )
        except (ValueError, IndexError, StopIteration) as e:
            raise LogParseError(f"Error parsing log line: {str(e)}") from e
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse Zscaler timestamp format: "Mon Jun 20 12:00:00 2022"
        
        Args:
            timestamp_str: Timestamp string
            
        Returns:
            datetime object
            
        Raises:
            LogParseError: If timestamp cannot be parsed
        """
        try:
            # Zscaler format: "Mon Jun 20 12:00:00 2022"
            return datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
        except ValueError as e:
            raise LogParseError(f"Invalid timestamp format: {timestamp_str}") from e
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL string (may include protocol or not)
            
        Returns:
            Domain name
        """
        if not url:
            return ""
        
        # Add protocol if missing for urlparse
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            # Remove port if present
            domain = domain.split(':')[0]
            return domain
        except Exception:
            # Fallback: try to extract domain manually
            # Remove protocol
            url = url.replace('http://', '').replace('https://', '')
            # Get first part before /
            domain = url.split('/')[0]
            # Remove port
            domain = domain.split(':')[0]
            return domain
    
    def _parse_int(self, value: str, default: int = 0) -> int:
        """
        Parse integer from string, returning default if invalid.
        
        Args:
            value: String value
            default: Default value if parsing fails
            
        Returns:
            Integer value
        """
        if not value or value.strip() == "":
            return default
        try:
            return int(value)
        except ValueError:
            return default

