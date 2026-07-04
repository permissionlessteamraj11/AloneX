# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import base64
from cryptography.fernet import Fernet
from NarzoxBots import config

class EncryptionService:
    def __init__(self, key: str):
        # Ensure the key is 32 bytes and base64 encoded for Fernet
        try:
            self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except:
            # Fallback if key is invalid: generate a stable key from the provided string
            import hashlib
            hkey = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
            self.fernet = Fernet(hkey)

    def encrypt(self, data: str) -> str:
        if not data: return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        if not data: return ""
        try:
            return self.fernet.decrypt(data.encode()).decode()
        except:
            return data # Return original if decryption fails (for migration/fallback)

encryption_service = EncryptionService(config.ENCRYPTION_KEY)
