from datetime import datetime, timedelta
from pathlib import Path
import jwt
from cryptography.hazmat.primitives import serialization

def generate_jwt():
    now = datetime.utcnow()
    payload = {
        "aud": "PRODUCTS_SRV",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "user_id": "100",
    }

    private_key_text = Path("private_key.pem").read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")

print(generate_jwt())

