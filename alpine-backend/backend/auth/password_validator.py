"""Enhanced password validation"""
import re
from typing import List, Tuple
from pydantic import validator
import hashlib

# Common password blacklist (top 10,000 most common passwords)
# In production, load from file or database
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "12345678", "12345",
    "1234567", "1234567890", "qwerty", "abc123", "password1",
    "123123", "admin", "letmein", "welcome", "monkey",
    "1234567890", "qwerty123", "password123", "admin123"
}


class PasswordValidator:
    """Password validation with strength scoring"""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL = True
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against requirements
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Length check
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long")
        
        # Uppercase check
        if PasswordValidator.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Lowercase check
        if PasswordValidator.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Numbers check
        if PasswordValidator.REQUIRE_NUMBERS and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        # Special characters check
        if PasswordValidator.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        # Common password check
        password_lower = password.lower()
        if password_lower in COMMON_PASSWORDS:
            errors.append("Password is too common. Please choose a more unique password")
        
        # Check for repeated characters (e.g., "aaaaaa")
        if re.search(r'(.)\1{3,}', password):
            errors.append("Password contains too many repeated characters")
        
        # Check for sequential characters (e.g., "12345", "abcde")
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            errors.append("Password contains sequential characters")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def calculate_strength(password: str) -> int:
        """
        Calculate password strength score (0-100)
        
        Returns:
            Strength score from 0 to 100
        """
        score = 0
        
        # Length scoring
        if len(password) >= 12:
            score += 20
        elif len(password) >= 8:
            score += 10
        
        # Character variety scoring
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_number = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        variety_count = sum([has_upper, has_lower, has_number, has_special])
        score += variety_count * 15
        
        # Length bonus
        if len(password) > 16:
            score += 10
        if len(password) > 20:
            score += 10
        
        # Penalties
        if password.lower() in COMMON_PASSWORDS:
            score = max(0, score - 50)
        
        if re.search(r'(.)\1{3,}', password):
            score = max(0, score - 20)
        
        return min(100, score)
    
    @staticmethod
    def get_strength_label(score: int) -> str:
        """Get human-readable strength label"""
        if score >= 80:
            return "Very Strong"
        elif score >= 60:
            return "Strong"
        elif score >= 40:
            return "Moderate"
        elif score >= 20:
            return "Weak"
        else:
            return "Very Weak"

