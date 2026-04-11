# Security utilities
# Currently not needed since we're not using authentication
# But keeping for future use

def generate_session_id():
    """Generate a unique session ID"""
    import uuid
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Hash a password (for future use)"""
    # This would be implemented when authentication is added
    pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password (for future use)"""
    # This would be implemented when authentication is added
    pass
