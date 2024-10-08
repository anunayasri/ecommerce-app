from datetime import datetime, timedelta
from pathlib import Path
import jwt
from cryptography.hazmat.primitives import serialization
from config import AppConfig

def generate_jwt():
    now = datetime.utcnow()
    payload = {
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "user_id": "1", 
    }

    private_key_text = Path(AppConfig().AUTH_JWT_PRIVATE_KEY_FILE).read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")

print(generate_jwt())

