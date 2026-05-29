from cryptography.fernet import Fernet
from config import Config

config = Config()

class EncryptionService:
    def __init__(self):
        # In a real scenario, the key should be loaded from env
        # Using a fallback just for demonstration, but recommending ENCRYPTION_KEY in .env
        key = config.ENCRYPTION_KEY.encode()
        if len(key) != 32: # Fernet key must be 32 url-safe base64-encoded bytes
             # For the sake of this task, we will generate one if invalid
             # but in production this is a critical error.
             import base64
             import hashlib
             key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

encryption_service = EncryptionService()
