import sys
import enum
from datetime import datetime, timedelta
from pathlib import Path
import jwt
from cryptography.hazmat.primitives import serialization

from config import AppConfig

class Role(enum.Enum):
    SELLER = "SELLER"
    BUYER = "BUYER"
    ORDER_SRV = "ORDER_SRV"

def generate_jwt(role: Role):
    now = datetime.utcnow()
    payload = {
        "aud": "PRODUCTS_SRV",
        "iat": now.timestamp(),
        "exp": (now + timedelta(hours=24)).timestamp(),
        "user_id": "1",
        "role": role.value,
    }

    conf = AppConfig()
    private_key_text = Path(conf.AUTH_JWT_PRIVATE_KEY_FILE).read_text()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode(),
        password=None,
    )
    return jwt.encode(payload=payload, key=private_key, algorithm="RS256")

if __name__ == '__main__':
    iss = Role(sys.argv[1])
    print(f"Generating jwt for iss: {iss}")
    print(generate_jwt(iss))

