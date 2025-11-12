"""TOTP (Time-based One-Time Password) implementation for 2FA"""
import pyotp
import qrcode
import io
import base64
from typing import Optional, Tuple
from datetime import datetime, timedelta
import secrets
import hashlib

# TOTP configuration
TOTP_ISSUER = "Alpine Analytics"
TOTP_INTERVAL = 30  # 30-second time windows


class TOTPManager:
    """Manage TOTP secrets and verification"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, email: str) -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL)
        return totp.provisioning_uri(
            name=email,
            issuer_name=TOTP_ISSUER
        )
    
    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """Generate QR code as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')
    
    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: TOTP secret
            token: Token to verify
            window: Time window tolerance (default: 1 = ±30 seconds)
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL)
            return totp.verify(token, valid_window=window)
        except Exception:
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """Generate backup codes for 2FA"""
        codes = []
        for _ in range(count):
            # Generate 8-digit backup code
            code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
            codes.append(code)
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code for storage"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_backup_code(hashed_codes: list[str], code: str) -> bool:
        """Verify backup code"""
        code_hash = TOTPManager.hash_backup_code(code)
        return code_hash in hashed_codes

