"""Kong API Gateway helper utilities."""
import uuid
from flask import request
from werkzeug.exceptions import Unauthorized
from flask_jwt_extended import decode_token


def get_user_id_from_kong():
    """
    Extract and validate user ID from JWT token in Authorization header.
    
    Kong validates the JWT token for authentication. This function decodes
    the token to extract the user ID from the 'sub' claim and checks if
    the token has been blacklisted (logged out).
    
    Returns:
        uuid.UUID: The validated user ID.
        
    Raises:
        Unauthorized: If the Authorization header is missing, token is invalid, or blacklisted.
    """
    # Get Authorization header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Unauthorized(description='Missing or invalid Authorization header')
    
    # Extract token
    token = auth_header.split(' ', 1)[1] if len(auth_header.split(' ')) > 1 else None
    
    if not token:
        raise Unauthorized(description='Missing JWT token')
    
    try:
        # Decode token to get claims (Kong already validated it)
        decoded = decode_token(token)
        user_id_str = decoded.get('sub')
        jti = decoded.get('jti')
        
        if not user_id_str:
            raise Unauthorized(description='Missing user ID in token')
        
        # Check if token is blacklisted (user logged out)
        if jti:
            from models import TokenBlacklist
            blacklisted = TokenBlacklist.query.filter_by(jti=jti).first()
            if blacklisted:
                raise Unauthorized(description='Token has been revoked (logged out)')
        
        user_id = uuid.UUID(user_id_str)
        return user_id
    except Unauthorized:
        # Re-raise Unauthorized exceptions
        raise
    except Exception as e:
        # Catch all other JWT decode errors and exceptions
        raise Unauthorized(description=f'Invalid token: {str(e)}')

