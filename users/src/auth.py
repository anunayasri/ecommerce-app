import hashlib

def verify_password(given_password: str, hashed_password: str) -> bool:
    given_password_hash = hashlib.sha256(given_password.encode('utf-8')).hexdigest()
    return given_password_hash == hashed_password

def hash_password(given_password: str) -> str:
    # Use sha256(without a salt)
    return hashlib.sha256(given_password.encode('utf-8')).hexdigest()
