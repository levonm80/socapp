"""AI routes."""
import uuid
from flask import Blueprint, request, jsonify
from models import LogEntry, LogFile
from services.ai_service import AIService
from utils.kong_helpers import get_user_id_from_kong

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()


@ai_bp.route('/log-summary/<log_file_id>', methods=['GET'])
def get_log_summary(log_file_id):
    """Get AI-generated log summary."""
    # Validate authentication
    get_user_id_from_kong()
    try:
        file_uuid = uuid.UUID(log_file_id)
    except ValueError:
        return jsonify({'error': 'Invalid file ID'}), 400
    
    log_file = LogFile.query.get(file_uuid)
    if not log_file:
        return jsonify({'error': 'Log file not found'}), 404
    
    summary = ai_service.generate_log_summary(log_file_id)
    
    return jsonify(summary), 200


@ai_bp.route('/explain-log-entry/<entry_id>', methods=['GET'])
def explain_log_entry(entry_id):
    """Get AI explanation for log entry."""
    # Validate authentication
    get_user_id_from_kong()
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        return jsonify({'error': 'Invalid entry ID'}), 400
    
    entry = LogEntry.query.get(entry_uuid)
    if not entry:
        return jsonify({'error': 'Log entry not found'}), 404
    
    explanation = ai_service.explain_log_entry(entry)
    
    return jsonify(explanation), 200


@ai_bp.route('/investigate', methods=['POST'])
def investigate():
    """AI investigation copilot."""
    # Validate authentication
    get_user_id_from_kong()
    data = request.get_json()
    
    if not data or not data.get('log_file_id') or not data.get('question'):
        return jsonify({'error': 'log_file_id and question required'}), 400
    
    log_file_id = data['log_file_id']
    question = data['question']
    
    try:
        file_uuid = uuid.UUID(log_file_id)
    except ValueError:
        return jsonify({'error': 'Invalid file ID'}), 400
    
    result = ai_service.investigate(file_uuid, question)
    
    return jsonify(result), 200
