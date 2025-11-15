"""Dashboard routes."""
import uuid
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_, text
from models import LogEntry, LogFile, UserRiskScore
from extensions import db
from utils.kong_helpers import get_user_id_from_kong

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    
    query = LogEntry.query
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    total_requests = query.count()
    blocked_events = query.filter(LogEntry.action == 'Blocked').count()
    malicious_urls = query.filter(LogEntry.is_anomalous == True).count()
    
    # High-risk users (risk_score > 70)
    risk_query = UserRiskScore.query
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            risk_query = risk_query.filter(UserRiskScore.log_file_id == file_uuid)
        except ValueError:
            pass
    high_risk_users = risk_query.filter(UserRiskScore.risk_score > 70).count()
    
    # Data transfer
    result = query.with_entities(func.sum(LogEntry.resp_size)).scalar()
    data_transfer_bytes = result or 0
    
    return jsonify({
        'total_requests': total_requests,
        'blocked_events': blocked_events,
        'malicious_urls': malicious_urls,
        'high_risk_users': high_risk_users,
        'data_transfer_bytes': data_transfer_bytes,
        'trends': {
            'total_requests_pct': 0.0,  # Would calculate from previous period
            'blocked_events_pct': 0.0
        }
    }), 200


@dashboard_bp.route('/timeline', methods=['GET'])
def get_timeline():
    """Get timeline data for charts."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    bucket_minutes = request.args.get('bucket_minutes', 15, type=int)
    hours = request.args.get('hours', 24, type=int)
    
    query = LogEntry.query
    
    # Determine time range based on whether log_file_id is provided
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            # Filter by log file
            query = query.filter(LogEntry.log_file_id == file_uuid)
            
            # Get the log file to use its date range
            log_file = LogFile.query.filter_by(id=file_uuid).first()
            if log_file and log_file.date_range_start and log_file.date_range_end:
                # Use the file's date range, but apply hours parameter relative to end date
                end_time = log_file.date_range_end
                start_time = end_time - timedelta(hours=hours)
                # Don't go before the file's start date
                if start_time < log_file.date_range_start:
                    start_time = log_file.date_range_start
                
                query = query.filter(
                    and_(
                        LogEntry.timestamp >= start_time,
                        LogEntry.timestamp <= end_time
                    )
                )
            # If file has no date range, don't filter by time (show all entries for this file)
        except ValueError:
            pass
    else:
        # No log_file_id: show all available data (no time filter)
        # This allows viewing historical data regardless of when it was logged
        pass
    
    # Group by time buckets (simplified - would use proper time bucketing in production)
    entries = query.all()
    
    buckets = {}
    for entry in entries:
        # Round to nearest bucket
        bucket_time = entry.timestamp.replace(
            minute=(entry.timestamp.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0
        )
        key = bucket_time.isoformat()
        
        if key not in buckets:
            buckets[key] = {'time': key, 'total': 0, 'blocked': 0}
        
        buckets[key]['total'] += 1
        if entry.action == 'Blocked':
            buckets[key]['blocked'] += 1
    
    return jsonify({'buckets': list(buckets.values())}), 200


@dashboard_bp.route('/timeline/v2', methods=['GET'])
def get_timeline_v2():
    """Get timeline data using PostgreSQL bucketing for better performance."""
    # Validate authentication
    get_user_id_from_kong()
    
    # Parse parameters
    log_file_id = request.args.get('log_file_id')
    bucket_minutes = request.args.get('bucket_minutes', 15, type=int)
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    debug_query = request.args.get('debug_query', 'false').lower() == 'true'
    
    # Validate bucket_minutes
    if bucket_minutes <= 0:
        return jsonify({'error': 'bucket_minutes must be greater than 0'}), 400
    if bucket_minutes > 1440:  # Max 24 hours
        return jsonify({'error': 'bucket_minutes cannot exceed 1440 (24 hours)'}), 400
    
    # Determine time range
    if start_time_str and end_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO 8601 format.'}), 400
        
        if start_time >= end_time:
            return jsonify({'error': 'start_time must be before end_time'}), 400
    elif log_file_id:
        # Use log file date range if available
        try:
            file_uuid = uuid.UUID(log_file_id)
            log_file = LogFile.query.filter_by(id=file_uuid).first()
            if log_file and log_file.date_range_start and log_file.date_range_end:
                start_time = log_file.date_range_start
                end_time = log_file.date_range_end
            else:
                # Fallback to last 24 hours
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=24)
        except ValueError:
            return jsonify({'error': 'Invalid log_file_id format'}), 400
    else:
        # Default to last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
    
    # Build SQL query with PostgreSQL bucketing
    # Round start_time and end_time to bucket boundaries
    start_time_truncated = start_time.replace(
        minute=(start_time.minute // bucket_minutes) * bucket_minutes,
        second=0,
        microsecond=0
    )
    end_time_truncated = end_time.replace(
        minute=(end_time.minute // bucket_minutes) * bucket_minutes,
        second=0,
        microsecond=0
    )
    
    # Build WHERE clause conditions (using quoted column name for PostgreSQL reserved word)
    # Use CAST instead of :: syntax to work with SQLAlchemy parameter binding
    where_conditions = ['"timestamp" >= CAST(:start_time AS timestamp)', '"timestamp" <= CAST(:end_time AS timestamp)']
    query_params = {
        'start_time': start_time_truncated.isoformat(),
        'end_time': end_time_truncated.isoformat(),
        'bucket_minutes': bucket_minutes
    }
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            where_conditions.append('log_file_id = :log_file_id')
            query_params['log_file_id'] = str(file_uuid)
        except ValueError:
            return jsonify({'error': 'Invalid log_file_id format'}), 400
    
    where_clause = ' AND '.join(where_conditions)
    
    # PostgreSQL query using generate_series for buckets and date_trunc for bucketing
    # Build interval string directly since bucket_minutes is validated as integer
    interval_str = f"{bucket_minutes} minutes"
    
    sql_query = text(f"""
        WITH buckets AS (
            SELECT generate_series(
                date_trunc('minute', CAST(:start_time AS timestamp)),
                date_trunc('minute', CAST(:end_time AS timestamp)),
                interval '{interval_str}'
            ) AS bucket_time
        ),
        counts AS (
            SELECT
                date_trunc('hour', "timestamp")
                    + floor(extract(minute FROM "timestamp") / :bucket_minutes) * interval '{interval_str}' AS bucket_time,
                count(*) AS log_count,
                count(*) FILTER (WHERE action = 'Blocked') AS blocked_count
            FROM log_entries
            WHERE {where_clause}
            GROUP BY bucket_time
        )
        SELECT
            b.bucket_time,
            COALESCE(c.log_count, 0) AS log_count,
            COALESCE(c.blocked_count, 0) AS blocked_count
        FROM buckets b
        LEFT JOIN counts c ON b.bucket_time = c.bucket_time
        ORDER BY b.bucket_time
    """)
    
    # Build a readable version of the query with parameters substituted for debugging
    final_query_readable = sql_query.text
    for param_name, param_value in query_params.items():
        # Replace parameter placeholders with actual values for logging
        if isinstance(param_value, str):
            # Quote strings properly for SQL
            final_query_readable = final_query_readable.replace(
                f':{param_name}', 
                f"'{param_value}'"
            )
        else:
            final_query_readable = final_query_readable.replace(
                f':{param_name}', 
                str(param_value)
            )
    
    logger.info(f"Timeline V2 Query:\n{final_query_readable}")
    logger.info(f"Query Parameters: {query_params}")
    
    # Also print to console for immediate visibility
    print("\n" + "="*80)
    print("TIMELINE V2 SQL QUERY:")
    print("="*80)
    print(final_query_readable)
    print("\nPARAMETERS:")
    for key, value in query_params.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    print("="*80 + "\n")
    
    try:
        result = db.session.execute(sql_query, query_params)
        buckets = []
        for row in result:
            buckets.append({
                'time': row.bucket_time.isoformat() if row.bucket_time else None,
                'bucket_time': row.bucket_time.isoformat() if row.bucket_time else None,
                'log_count': int(row.log_count) if row.log_count else 0,
                'total': int(row.log_count) if row.log_count else 0,  # Alias for backward compatibility
                'blocked_count': int(row.blocked_count) if row.blocked_count else 0,
                'blocked': int(row.blocked_count) if row.blocked_count else 0  # Alias for backward compatibility
            })
        
        response_data = {'buckets': buckets}
        
        # Include query in response if debug_query=true
        if debug_query:
            response_data['debug'] = {
                'query': final_query_readable,
                'query_template': sql_query.text,
                'parameters': query_params,
                'where_clause': where_clause,
                'interval_str': interval_str
            }
        
        return jsonify(response_data), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            'error': f'Database query failed: {str(e)}',
            'details': error_details
        }), 500


@dashboard_bp.route('/top-categories', methods=['GET'])
def get_top_categories():
    """Get top URL categories."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    limit = request.args.get('limit', 10, type=int)
    
    query = LogEntry.query.with_entities(
        LogEntry.url_cat,
        func.count(LogEntry.id).label('count')
    ).group_by(LogEntry.url_cat)
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    results = query.order_by(func.count(LogEntry.id).desc()).limit(limit).all()
    total = sum(r.count for r in results)
    
    categories = []
    for name, count in results:
        categories.append({
            'name': name or 'Unknown',
            'count': count,
            'percentage': (count / total * 100) if total > 0 else 0
        })
    
    return jsonify({'categories': categories}), 200


@dashboard_bp.route('/top-domains', methods=['GET'])
def get_top_domains():
    """Get top domains."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    limit = request.args.get('limit', 10, type=int)
    
    query = LogEntry.query.with_entities(
        LogEntry.domain,
        func.count(LogEntry.id).label('count'),
        func.sum(func.cast(LogEntry.action == 'Blocked', db.Integer)).label('blocked_count')
    ).group_by(LogEntry.domain)
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    results = query.order_by(func.count(LogEntry.id).desc()).limit(limit).all()
    
    domains = []
    for domain, count, blocked_count in results:
        domains.append({
            'domain': domain or 'Unknown',
            'count': count,
            'blocked_count': blocked_count or 0
        })
    
    return jsonify({'domains': domains}), 200


@dashboard_bp.route('/top-users', methods=['GET'])
def get_top_users():
    # Validate authentication
    get_user_id_from_kong()
    """Get top users by request count."""
    log_file_id = request.args.get('log_file_id')
    limit = request.args.get('limit', 10, type=int)
    
    query = LogEntry.query.with_entities(
        LogEntry.department,
        func.count(LogEntry.id).label('request_count')
    ).group_by(LogEntry.department)
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    results = query.order_by(func.count(LogEntry.id).desc()).limit(limit).all()
    
    users = []
    for identifier, request_count in results:
        # Get risk score if available
        risk_score = 0
        if log_file_id:
            try:
                file_uuid = uuid.UUID(log_file_id)
                risk = UserRiskScore.query.filter_by(
                    log_file_id=file_uuid,
                    user_identifier=identifier or ''
                ).first()
                if risk:
                    risk_score = risk.risk_score
            except ValueError:
                pass
        
        users.append({
            'identifier': identifier or 'Unknown',
            'request_count': request_count,
            'risk_score': risk_score
        })
    
    return jsonify({'users': users}), 200


@dashboard_bp.route('/recent-logs', methods=['GET'])
def get_recent_logs():
    """Get recent log entries."""
    # Validate authentication
    get_user_id_from_kong()
    log_file_id = request.args.get('log_file_id')
    limit = request.args.get('limit', 10, type=int)
    
    query = LogEntry.query.order_by(LogEntry.timestamp.desc())
    
    if log_file_id:
        try:
            file_uuid = uuid.UUID(log_file_id)
            query = query.filter(LogEntry.log_file_id == file_uuid)
        except ValueError:
            pass
    
    entries = query.limit(limit).all()
    
    return jsonify({'entries': [e.to_dict() for e in entries]}), 200
