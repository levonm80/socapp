"""Log routes."""
import uuid
import zipfile
import io
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_, func
from models import LogFile, LogEntry, User
from extensions import db
from services.log_parser import ZscalerLogParser, LogParseError
from services.anomaly_detector import AnomalyDetector
from services.risk_scorer import calculate_user_risk_scores
from models import UserRiskScore
from utils.kong_helpers import get_user_id_from_kong

logs_bp = Blueprint('logs', __name__)
parser = ZscalerLogParser()
detector = AnomalyDetector()


@logs_bp.route('/upload', methods=['POST'])
def upload_log():
    """Upload and process log file asynchronously."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get user ID from Kong-injected header
    user_id = get_user_id_from_kong()
    
    # Read file content into memory before returning response
    file.seek(0)
    file_content = file.read()
    file_filename = file.filename
    
    # Create log file record
    log_file = LogFile(
        filename=file_filename,
        uploaded_by=user_id,
        status='processing'
    )
    db.session.add(log_file)
    db.session.commit()
    
    log_file_id = log_file.id
    
    # Process file asynchronously in background thread
    # Pass app context to thread
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_process_log_file_async,
        args=(app, log_file_id, file_content, file_filename),
        daemon=True
    )
    thread.start()
    
    # Return immediately with 200 status
    return jsonify({
        'log_file_id': str(log_file_id),
        'status': 'processing',
        'message': 'File uploaded successfully. Processing in background.'
    }), 200


def _process_log_file_async(app, log_file_id: uuid.UUID, file_content: bytes, filename: str):
    """Process log file asynchronously in background thread.
    
    Args:
        app: Flask application instance (for app context)
        log_file_id: UUID of the log file record
        file_content: File content as bytes
        filename: Original filename
    """
    with app.app_context():
        # Create a file-like object from bytes
        file_obj = io.BytesIO(file_content)
        file_obj.filename = filename
        
        try:
            _process_log_file(log_file_id, file_obj)
        except Exception as e:
            # Update status to failed
            log_file = LogFile.query.get(log_file_id)
            if log_file:
                log_file.status = 'failed'
                db.session.commit()
            # Log error for debugging
            app.logger.error(f"Error processing log file {log_file_id}: {str(e)}", exc_info=True)


def _process_log_file(log_file_id: uuid.UUID, file):
    """Process log file: parse, detect anomalies, calculate risk scores.
    
    Supports both regular files and zip archives. If zip, extracts and processes all files.
    Processes entries in batches of 1000 for memory efficiency.
    
    Note: This function assumes it's called within an app context.
    """
    log_file = LogFile.query.get(log_file_id)
    if not log_file:
        return
    
    BATCH_SIZE = 1000
    parsed_batch = []
    recent_entries_by_ip = {}  # For burst detection
    all_timestamps = []  # Track timestamps for date range calculation
    total_processed = 0
    
    def process_batch(batch_entries):
        """Process a batch of parsed entries and insert into DB."""
        nonlocal total_processed
        
        if not batch_entries:
            return
        
        log_entries = []
        for parsed in batch_entries:
            # Get recent entries for burst detection
            recent = recent_entries_by_ip.get(parsed.client_ip, [])
            anomaly_result = detector.detect_anomalies(parsed, recent)
            
            # Create LogEntry
            log_entry = LogEntry(
                log_file_id=log_file_id,
                timestamp=parsed.timestamp,
                location=parsed.location,
                protocol=parsed.protocol,
                url=parsed.url,
                domain=parsed.domain,
                action=parsed.action,
                app_name=parsed.app_name,
                app_class=parsed.app_class,
                throttle_req_size=parsed.throttle_req_size,
                throttle_resp_size=parsed.throttle_resp_size,
                req_size=parsed.req_size,
                resp_size=parsed.resp_size,
                url_class=parsed.url_class,
                url_supercat=parsed.url_supercat,
                url_cat=parsed.url_cat,
                dlp_dict=parsed.dlp_dict,
                dlp_eng=parsed.dlp_eng,
                dlp_hits=parsed.dlp_hits,
                file_class=parsed.file_class,
                file_type=parsed.file_type,
                location2=parsed.location2,
                department=parsed.department,
                client_ip=parsed.client_ip,
                server_ip=parsed.server_ip,
                http_method=parsed.http_method,
                http_status=parsed.http_status,
                user_agent=parsed.user_agent,
                threat_category=parsed.threat_category,
                fw_filter=parsed.fw_filter,
                fw_rule=parsed.fw_rule,
                policy_type=parsed.policy_type,
                reason=parsed.reason,
                is_anomalous=anomaly_result.is_anomalous,
                anomaly_type=anomaly_result.anomaly_type,
                anomaly_reason=anomaly_result.reason,
                anomaly_confidence=anomaly_result.confidence
            )
            log_entries.append(log_entry)
            
            # Update recent entries for burst detection
            if parsed.client_ip not in recent_entries_by_ip:
                recent_entries_by_ip[parsed.client_ip] = []
            recent_entries_by_ip[parsed.client_ip].append(parsed)
            # Keep only last 20 entries per IP
            if len(recent_entries_by_ip[parsed.client_ip]) > 20:
                recent_entries_by_ip[parsed.client_ip].pop(0)
            
            # Track timestamps for date range
            all_timestamps.append(parsed.timestamp)
        
        # Bulk insert batch
        db.session.bulk_save_objects(log_entries)
        db.session.commit()
        
        total_processed += len(log_entries)
        
        # Update progress periodically
        log_file.total_entries = total_processed
        db.session.commit()
    
    try:
        # Check if file is a zip archive (check both extension and magic bytes)
        filename = file.filename.lower() if hasattr(file, 'filename') else ''
        has_zip_extension = filename.endswith('.zip') if filename else False
        
        # Check file content to see if it's actually a zip file
        file.seek(0)
        file_start = file.read(4)
        file.seek(0)
        is_zip_file = file_start[:2] == b'PK'  # ZIP files start with PK (PKZIP signature)
        
        is_zip = has_zip_extension or is_zip_file
        
        if is_zip:
            # Process zip file: extract and process all files
            file.seek(0)  # Reset file pointer
            zip_data = file.read()
            zip_buffer = io.BytesIO(zip_data)
            
            try:
                zip_ref = zipfile.ZipFile(zip_buffer, 'r')
            except zipfile.BadZipFile:
                raise ValueError("Invalid or corrupted zip file")
            
            with zip_ref:
                # Get list of files in zip
                file_list = zip_ref.namelist()
                
                # Process each file in the zip
                for zip_file_name in file_list:
                    # Skip directories and non-log files
                    if zip_file_name.endswith('/'):
                        continue
                    
                    # Only process .csv, .txt, .log files
                    if not any(zip_file_name.lower().endswith(ext) for ext in ['.csv', '.txt', '.log']):
                        continue
                    
                    try:
                        # Read file from zip
                        file_content = zip_ref.read(zip_file_name)
                        
                        # Try to decode as UTF-8 first, fallback to latin-1
                        try:
                            file_text = file_content.decode('utf-8')
                        except UnicodeDecodeError:
                            file_text = file_content.decode('latin-1', errors='ignore')
                        
                        # Parse file line by line in batches
                        for line_num, line in enumerate(file_text.splitlines(), 1):
                            line = line.strip()
                            if not line:
                                continue
                            
                            try:
                                parsed = parser.parse_line(line)
                                parsed_batch.append(parsed)
                                
                                # Process batch when it reaches BATCH_SIZE
                                if len(parsed_batch) >= BATCH_SIZE:
                                    process_batch(parsed_batch)
                                    parsed_batch = []
                            except LogParseError:
                                continue  # Skip invalid lines
                    except Exception as e:
                        # Log error but continue processing other files
                        print(f"Error processing {zip_file_name} in zip: {str(e)}")
                        continue
        else:
            # Process regular file line by line
            file.seek(0)  # Reset file pointer
            for line_num, line in enumerate(file, 1):
                try:
                    line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    # Try other encodings
                    try:
                        line = line.decode('latin-1').strip()
                    except:
                        continue
                
                if not line:
                    continue
                
                try:
                    parsed = parser.parse_line(line)
                    parsed_batch.append(parsed)
                    
                    # Process batch when it reaches BATCH_SIZE
                    if len(parsed_batch) >= BATCH_SIZE:
                        process_batch(parsed_batch)
                        parsed_batch = []
                except LogParseError:
                    continue  # Skip invalid lines
        
        # Process remaining entries in the last batch
        if parsed_batch:
            process_batch(parsed_batch)
        
        # Calculate date range from all timestamps
        if all_timestamps:
            log_file.date_range_start = min(all_timestamps)
            log_file.date_range_end = max(all_timestamps)
        
        # Calculate risk scores - need to query all entries for this log file
        # Refresh log_file to get updated total_entries
        db.session.refresh(log_file)
        log_entries_for_risk = LogEntry.query.filter_by(log_file_id=log_file_id).all()
        
        if log_entries_for_risk:
            risk_scores = calculate_user_risk_scores(log_file_id, log_entries_for_risk)
            for user_id, score_data in risk_scores.items():
                risk_score = UserRiskScore(
                    log_file_id=log_file_id,
                    user_identifier=user_id,
                    risk_score=score_data['risk_score'],
                    anomaly_count=score_data['anomaly_count'],
                    blocked_count=score_data['blocked_count'],
                    malicious_domain_count=score_data['malicious_domain_count'],
                    score_metadata=score_data['metadata']
                )
                db.session.add(risk_score)
        
        log_file.status = 'completed'
        db.session.commit()
        
    except Exception as e:
        log_file.status = 'failed'
        db.session.commit()
        raise


@logs_bp.route('/files', methods=['GET'])
def list_log_files():
    """List uploaded log files."""
    # Validate authentication
    get_user_id_from_kong()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    files = LogFile.query.order_by(LogFile.uploaded_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        'files': [f.to_dict() for f in files.items],
        'total': files.total,
        'page': page,
        'limit': limit
    }), 200


@logs_bp.route('/files/<file_id>', methods=['GET'])
def get_log_file(file_id):
    """Get log file details."""
    # Validate authentication
    get_user_id_from_kong()
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        return jsonify({'error': 'Invalid file ID'}), 400
    
    log_file = LogFile.query.get(file_uuid)
    if not log_file:
        return jsonify({'error': 'Log file not found'}), 404
    
    return jsonify(log_file.to_dict()), 200


@logs_bp.route('/files/<file_id>/preview', methods=['GET'])
def preview_log_file(file_id):
    """Get preview of log file (first N lines)."""
    # Validate authentication
    get_user_id_from_kong()
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        return jsonify({'error': 'Invalid file ID'}), 400
    
    log_file = LogFile.query.get(file_uuid)
    if not log_file:
        return jsonify({'error': 'Log file not found'}), 404
    
    lines = request.args.get('lines', 10, type=int)
    
    # Get first N entries
    entries = LogEntry.query.filter_by(log_file_id=file_uuid)\
        .order_by(LogEntry.timestamp)\
        .limit(lines).all()
    
    preview = []
    for entry in entries:
        preview.append(f"{entry.timestamp.isoformat()},{entry.client_ip},{entry.url},{entry.action}")
    
    return jsonify({'preview': preview}), 200


@logs_bp.route('/entries', methods=['GET'])
def list_log_entries():
    """List log entries with filters."""
    # Validate authentication
    get_user_id_from_kong()
    # Parse filters
    log_file_id = request.args.get('log_file_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    action = request.args.get('action')
    category = request.args.get('category')
    threat_category = request.args.get('threat_category')
    user_identifier = request.args.get('user_identifier')
    is_anomalous = request.args.get('is_anomalous')
    domain = request.args.get('domain')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    # Build query
    query = LogEntry.query
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(LogEntry.timestamp >= start_dt)
        except ValueError:
            pass
    
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(LogEntry.timestamp <= end_dt)
        except ValueError:
            pass
    
    if action:
        query = query.filter(LogEntry.action == action)
    
    if category:
        query = query.filter(LogEntry.url_cat == category)
    
    if threat_category:
        query = query.filter(LogEntry.threat_category == threat_category)
    
    if user_identifier:
        query = query.filter(
            or_(
                LogEntry.department == user_identifier,
                LogEntry.client_ip == user_identifier
            )
        )
    
    if is_anomalous is not None:
        is_anom = is_anomalous.lower() == 'true'
        query = query.filter(LogEntry.is_anomalous == is_anom)
    
    if domain:
        query = query.filter(LogEntry.domain == domain)
    
    # Paginate
    entries = query.order_by(LogEntry.timestamp.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        'entries': [e.to_dict() for e in entries.items],
        'total': entries.total,
        'page': page,
        'limit': limit
    }), 200


@logs_bp.route('/entries/<entry_id>', methods=['GET'])
def get_log_entry(entry_id):
    """Get single log entry."""
    # Validate authentication
    get_user_id_from_kong()
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        return jsonify({'error': 'Invalid entry ID'}), 400
    
    entry = LogEntry.query.get(entry_uuid)
    if not entry:
        return jsonify({'error': 'Log entry not found'}), 404
    
    return jsonify(entry.to_dict()), 200
