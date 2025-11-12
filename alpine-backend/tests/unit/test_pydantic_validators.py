"""Unit tests for Pydantic validators"""
import pytest
from pydantic import ValidationError
from backend.api.users import UpdateProfileRequest
from backend.api.subscriptions import UpgradeRequest
from backend.api.notifications import MarkReadRequest
from backend.api.two_factor import Enable2FARequest, Verify2FARequest
from backend.api.auth_2fa import Verify2FALoginRequest


class TestUpdateProfileRequest:
    """Test UpdateProfileRequest validators"""
    
    def test_valid_full_name(self):
        """Test valid full name"""
        request = UpdateProfileRequest(full_name="John Doe")
        assert request.full_name == "John Doe"
    
    def test_full_name_too_short(self):
        """Test full name too short"""
        with pytest.raises(ValidationError):
            UpdateProfileRequest(full_name="")
    
    def test_full_name_with_html(self):
        """Test full name with HTML (should be sanitized)"""
        request = UpdateProfileRequest(full_name="<script>alert('xss')</script>")
        # HTML should be escaped by sanitizer
        assert "<script>" not in request.full_name
    
    def test_valid_email(self):
        """Test valid email"""
        request = UpdateProfileRequest(email="test@example.com")
        assert request.email == "test@example.com"
    
    def test_invalid_email_format(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError):
            UpdateProfileRequest(email="not-an-email")
    
    def test_email_normalization(self):
        """Test email normalization to lowercase"""
        request = UpdateProfileRequest(email="Test@Example.COM")
        assert request.email == "test@example.com"
    
    def test_both_fields_none(self):
        """Test both fields can be None"""
        request = UpdateProfileRequest()
        assert request.full_name is None
        assert request.email is None


class TestUpgradeRequest:
    """Test UpgradeRequest validators"""
    
    def test_valid_starter_tier(self):
        """Test valid starter tier"""
        request = UpgradeRequest(tier="starter")
        assert request.tier == "starter"
    
    def test_valid_pro_tier(self):
        """Test valid pro tier"""
        request = UpgradeRequest(tier="pro")
        assert request.tier == "pro"
    
    def test_valid_elite_tier(self):
        """Test valid elite tier"""
        request = UpgradeRequest(tier="elite")
        assert request.tier == "elite"
    
    def test_tier_normalization(self):
        """Test tier normalization to lowercase"""
        request = UpgradeRequest(tier="PRO")
        assert request.tier == "pro"
    
    def test_invalid_tier(self):
        """Test invalid tier"""
        with pytest.raises(ValidationError):
            UpgradeRequest(tier="premium")
    
    def test_tier_with_whitespace(self):
        """Test tier with whitespace"""
        request = UpgradeRequest(tier="  pro  ")
        assert request.tier == "pro"


class TestMarkReadRequest:
    """Test MarkReadRequest validators"""
    
    def test_valid_notification_ids(self):
        """Test valid notification IDs"""
        request = MarkReadRequest(notification_ids=["notif-1", "notif-2"])
        assert len(request.notification_ids) == 2
    
    def test_empty_notification_ids(self):
        """Test empty notification IDs list"""
        with pytest.raises(ValidationError):
            MarkReadRequest(notification_ids=[])
    
    def test_too_many_notification_ids(self):
        """Test too many notification IDs"""
        ids = [f"notif-{i}" for i in range(101)]
        with pytest.raises(ValidationError):
            MarkReadRequest(notification_ids=ids)
    
    def test_invalid_notification_id_format(self):
        """Test invalid notification ID format"""
        with pytest.raises(ValidationError):
            MarkReadRequest(notification_ids=["notif<script>"])
    
    def test_notification_id_too_long(self):
        """Test notification ID too long"""
        long_id = "a" * 101
        with pytest.raises(ValidationError):
            MarkReadRequest(notification_ids=[long_id])


class TestEnable2FARequest:
    """Test Enable2FARequest validators"""
    
    def test_valid_6_digit_token(self):
        """Test valid 6-digit TOTP token"""
        request = Enable2FARequest(token="123456")
        assert request.token == "123456"
    
    def test_token_too_short(self):
        """Test token too short"""
        with pytest.raises(ValidationError):
            Enable2FARequest(token="12345")
    
    def test_token_too_long(self):
        """Test token too long"""
        with pytest.raises(ValidationError):
            Enable2FARequest(token="1234567")
    
    def test_token_with_letters(self):
        """Test token with letters (invalid)"""
        with pytest.raises(ValidationError):
            Enable2FARequest(token="12345a")
    
    def test_token_with_special_characters(self):
        """Test token with special characters (invalid)"""
        with pytest.raises(ValidationError):
            Enable2FARequest(token="123-45")


class TestVerify2FARequest:
    """Test Verify2FARequest validators"""
    
    def test_valid_6_digit_token(self):
        """Test valid 6-digit TOTP token"""
        request = Verify2FARequest(token="123456")
        assert request.token == "123456"
    
    def test_valid_backup_code(self):
        """Test valid backup code"""
        request = Verify2FARequest(token="ABCD1234")
        assert request.token == "ABCD1234"
    
    def test_token_too_short(self):
        """Test token too short"""
        with pytest.raises(ValidationError):
            Verify2FARequest(token="12345")
    
    def test_token_too_long(self):
        """Test token too long"""
        long_token = "a" * 13
        with pytest.raises(ValidationError):
            Verify2FARequest(token=long_token)
    
    def test_token_with_special_characters(self):
        """Test token with special characters (invalid)"""
        with pytest.raises(ValidationError):
            Verify2FARequest(token="123-45")


class TestVerify2FALoginRequest:
    """Test Verify2FALoginRequest validators"""
    
    def test_valid_request(self):
        """Test valid 2FA login request"""
        request = Verify2FALoginRequest(email="test@example.com", token="123456")
        assert request.email == "test@example.com"
        assert request.token == "123456"
    
    def test_email_normalization(self):
        """Test email normalization"""
        request = Verify2FALoginRequest(email="Test@Example.COM", token="123456")
        assert request.email == "test@example.com"
    
    def test_invalid_email(self):
        """Test invalid email"""
        with pytest.raises(ValidationError):
            Verify2FALoginRequest(email="not-an-email", token="123456")
    
    def test_invalid_token_format(self):
        """Test invalid token format"""
        with pytest.raises(ValidationError):
            Verify2FALoginRequest(email="test@example.com", token="123-45")
    
    def test_token_too_short(self):
        """Test token too short"""
        with pytest.raises(ValidationError):
            Verify2FALoginRequest(email="test@example.com", token="12345")

