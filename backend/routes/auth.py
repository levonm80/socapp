"""Authentication routes."""
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt
from models import User, TokenBlacklist
from extensions import db
from utils.kong_helpers import get_user_id_from_kong
from config import Config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email']
    password = data['password']
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create access token with additional claims for Kong
    jti = str(uuid.uuid4())  # Unique token ID for blacklist tracking
    additional_claims = {
        "iss": "flask-jwt",  # Issuer claim for Kong JWT plugin
        "jti": jti  # JWT ID for token revocation
    }
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )
    
    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint - adds token to blacklist."""
    # Get user ID and JWT claims
    user_id = get_user_id_from_kong()
    
    # Get JWT claims from the decoded token
    from flask import request as flask_request
    from flask_jwt_extended import decode_token
    
    auth_header = flask_request.headers.get('Authorization', '')
    token = auth_header.split(' ', 1)[1] if len(auth_header.split(' ')) > 1 else None
    
    if token:
        try:
            decoded = decode_token(token)
            jti = decoded.get('jti')
            exp_timestamp = decoded.get('exp')
            
            if jti and exp_timestamp:
                # Add token to blacklist
                expires_at = datetime.fromtimestamp(exp_timestamp)
                blacklisted_token = TokenBlacklist(
                    jti=jti,
                    token_type='access',
                    user_id=user_id,
                    expires_at=expires_at
                )
                db.session.add(blacklisted_token)
                db.session.commit()
        except Exception as e:
            # If we can't blacklist, still return success (client-side logout)
            pass
    
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user."""
    # Get user ID from Kong-injected header
    user_id = get_user_id_from_kong()
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200
