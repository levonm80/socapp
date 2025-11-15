"""Health check routes."""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service monitoring."""
    return jsonify({
        'status': 'healthy',
        'service': 'socapp-backend'
    }), 200

