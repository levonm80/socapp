"""Anomalies routes."""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from models import LogEntry
from extensions import db
from utils.kong_helpers import get_user_id_from_kong

anomalies_bp = Blueprint('anomalies', __name__)


@anomalies_bp.route('', methods=['GET'])
def list_anomalies():
    """List anomalies."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    anomaly_type = request.args.get('anomaly_type')
    min_confidence = request.args.get('min_confidence', 0.5, type=float)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    query = LogEntry.query.filter(LogEntry.is_anomalous == True)
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    if anomaly_type:
        query = query.filter(LogEntry.anomaly_type == anomaly_type)
    
    if min_confidence:
        query = query.filter(LogEntry.anomaly_confidence >= min_confidence)
    
    entries = query.order_by(LogEntry.timestamp.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    anomalies = []
    for entry in entries.items:
        anomalies.append({
            'entry_id': str(entry.id),
            'log_entry': entry.to_dict(),
            'anomaly_type': entry.anomaly_type,
            'reason': entry.anomaly_reason,
            'confidence': entry.anomaly_confidence
        })
    
    return jsonify({
        'anomalies': anomalies,
        'total': entries.total
    }), 200


@anomalies_bp.route('/timeline', methods=['GET'])
def get_anomaly_timeline():
    """Get anomaly timeline."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    bucket_minutes = request.args.get('bucket_minutes', 15, type=int)
    
    query = LogEntry.query.filter(LogEntry.is_anomalous == True)
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    entries = query.all()
    
    buckets = {}
    for entry in entries:
        bucket_time = entry.timestamp.replace(
            minute=(entry.timestamp.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0
        )
        key = bucket_time.isoformat()
        
        if key not in buckets:
            buckets[key] = {
                'time': key,
                'count': 0,
                'by_type': {}
            }
        
        buckets[key]['count'] += 1
        anomaly_type = entry.anomaly_type or 'unknown'
        buckets[key]['by_type'][anomaly_type] = buckets[key]['by_type'].get(anomaly_type, 0) + 1
    
    return jsonify({'buckets': list(buckets.values())}), 200
