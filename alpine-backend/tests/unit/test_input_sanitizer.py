"""Unit tests for input sanitization functions"""
import pytest
from backend.core.input_sanitizer import (
    sanitize_string,
    sanitize_email,
    sanitize_symbol,
    sanitize_action,
    sanitize_tier,
    sanitize_integer,
    sanitize_float,
    sanitize_path_traversal
)


class TestSanitizeString:
    """Test sanitize_string function"""
    
    def test_basic_sanitization(self):
        """Test basic string sanitization"""
        result = sanitize_string("Hello World")
        assert result == "Hello World"
    
    def test_html_escaping(self):
        """Test HTML escaping for XSS prevention"""
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_null_bytes_removal(self):
        """Test null byte removal"""
        result = sanitize_string("test\x00string")
        assert "\x00" not in result
        assert result == "teststring"
    
    def test_control_characters_removal(self):
        """Test control character removal"""
        result = sanitize_string("test\x01\x02\x03string")
        assert "\x01" not in result
        assert "\x02" not in result
        assert "\x03" not in result
    
    def test_whitespace_trimming(self):
        """Test whitespace trimming"""
        result = sanitize_string("  test  ")
        assert result == "test"
    
    def test_max_length_truncation(self):
        """Test max length truncation"""
        result = sanitize_string("a" * 100, max_length=10)
        assert len(result) == 10
    
    def test_non_string_input(self):
        """Test non-string input conversion"""
        result = sanitize_string(123)
        assert result == "123"
    
    def test_empty_string(self):
        """Test empty string handling"""
        result = sanitize_string("")
        assert result == ""
    
    def test_special_characters(self):
        """Test special characters are escaped"""
        result = sanitize_string("Test & < > \" ' /")
        assert "&amp;" in result
        assert "&lt;" in result
        assert "&gt;" in result


class TestSanitizeEmail:
    """Test sanitize_email function"""
    
    def test_valid_email(self):
        """Test valid email sanitization"""
        result = sanitize_email("Test@Example.COM")
        assert result == "test@example.com"
    
    def test_email_with_whitespace(self):
        """Test email with whitespace"""
        result = sanitize_email("  test@example.com  ")
        assert result == "test@example.com"
    
    def test_invalid_email_format(self):
        """Test invalid email format"""
        with pytest.raises(ValueError, match="Invalid email format"):
            sanitize_email("not-an-email")
    
    def test_email_too_long(self):
        """Test email exceeding RFC 5321 limit"""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValueError, match="Email address too long"):
            sanitize_email(long_email)
    
    def test_non_string_email(self):
        """Test non-string email input"""
        with pytest.raises(ValueError, match="Email must be a string"):
            sanitize_email(123)
    
    def test_email_with_plus(self):
        """Test email with plus sign"""
        result = sanitize_email("test+tag@example.com")
        assert result == "test+tag@example.com"
    
    def test_email_with_dots(self):
        """Test email with dots"""
        result = sanitize_email("test.name@example.co.uk")
        assert result == "test.name@example.co.uk"


class TestSanitizeSymbol:
    """Test sanitize_symbol function"""
    
    def test_valid_symbol(self):
        """Test valid symbol sanitization"""
        result = sanitize_symbol("aapl")
        assert result == "AAPL"
    
    def test_symbol_with_hyphen(self):
        """Test symbol with hyphen"""
        result = sanitize_symbol("btc-usd")
        assert result == "BTC-USD"
    
    def test_symbol_with_underscore(self):
        """Test symbol with underscore"""
        result = sanitize_symbol("test_symbol")
        assert result == "TEST_SYMBOL"
    
    def test_invalid_symbol_characters(self):
        """Test invalid symbol characters"""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            sanitize_symbol("AAPL!")
    
    def test_symbol_too_long(self):
        """Test symbol exceeding length limit"""
        long_symbol = "A" * 21
        with pytest.raises(ValueError, match="Symbol too long"):
            sanitize_symbol(long_symbol)
    
    def test_non_string_symbol(self):
        """Test non-string symbol input"""
        with pytest.raises(ValueError, match="Symbol must be a string"):
            sanitize_symbol(123)
    
    def test_symbol_with_whitespace(self):
        """Test symbol with whitespace"""
        result = sanitize_symbol("  aapl  ")
        assert result == "AAPL"


class TestSanitizeAction:
    """Test sanitize_action function"""
    
    def test_valid_buy_action(self):
        """Test valid BUY action"""
        result = sanitize_action("buy")
        assert result == "BUY"
    
    def test_valid_sell_action(self):
        """Test valid SELL action"""
        result = sanitize_action("sell")
        assert result == "SELL"
    
    def test_invalid_action(self):
        """Test invalid action"""
        with pytest.raises(ValueError, match="Invalid action"):
            sanitize_action("HOLD")
    
    def test_action_with_whitespace(self):
        """Test action with whitespace"""
        result = sanitize_action("  buy  ")
        assert result == "BUY"
    
    def test_non_string_action(self):
        """Test non-string action input"""
        with pytest.raises(ValueError, match="Action must be a string"):
            sanitize_action(123)


class TestSanitizeTier:
    """Test sanitize_tier function"""
    
    def test_valid_starter_tier(self):
        """Test valid starter tier"""
        result = sanitize_tier("STARTER")
        assert result == "starter"
    
    def test_valid_pro_tier(self):
        """Test valid pro tier"""
        result = sanitize_tier("PRO")
        assert result == "pro"
    
    def test_valid_elite_tier(self):
        """Test valid elite tier"""
        result = sanitize_tier("ELITE")
        assert result == "elite"
    
    def test_invalid_tier(self):
        """Test invalid tier"""
        with pytest.raises(ValueError, match="Invalid tier"):
            sanitize_tier("premium")
    
    def test_tier_with_whitespace(self):
        """Test tier with whitespace"""
        result = sanitize_tier("  pro  ")
        assert result == "pro"
    
    def test_non_string_tier(self):
        """Test non-string tier input"""
        with pytest.raises(ValueError, match="Tier must be a string"):
            sanitize_tier(123)


class TestSanitizeInteger:
    """Test sanitize_integer function"""
    
    def test_valid_integer(self):
        """Test valid integer"""
        result = sanitize_integer("123")
        assert result == 123
    
    def test_integer_with_min_value(self):
        """Test integer with minimum value constraint"""
        result = sanitize_integer(10, min_value=5)
        assert result == 10
    
    def test_integer_below_min_value(self):
        """Test integer below minimum value"""
        with pytest.raises(ValueError, match="must be at least"):
            sanitize_integer(5, min_value=10)
    
    def test_integer_with_max_value(self):
        """Test integer with maximum value constraint"""
        result = sanitize_integer(10, max_value=20)
        assert result == 10
    
    def test_integer_above_max_value(self):
        """Test integer above maximum value"""
        with pytest.raises(ValueError, match="must be at most"):
            sanitize_integer(30, max_value=20)
    
    def test_invalid_integer(self):
        """Test invalid integer input"""
        with pytest.raises(ValueError, match="Invalid integer value"):
            sanitize_integer("not-a-number")
    
    def test_float_as_integer(self):
        """Test float input for integer"""
        with pytest.raises(ValueError, match="Invalid integer value"):
            sanitize_integer(12.5)


class TestSanitizeFloat:
    """Test sanitize_float function"""
    
    def test_valid_float(self):
        """Test valid float"""
        result = sanitize_float("12.5")
        assert result == 12.5
    
    def test_float_with_min_value(self):
        """Test float with minimum value constraint"""
        result = sanitize_float(10.5, min_value=5.0)
        assert result == 10.5
    
    def test_float_below_min_value(self):
        """Test float below minimum value"""
        with pytest.raises(ValueError, match="must be at least"):
            sanitize_float(3.0, min_value=5.0)
    
    def test_float_with_max_value(self):
        """Test float with maximum value constraint"""
        result = sanitize_float(10.5, max_value=20.0)
        assert result == 10.5
    
    def test_float_above_max_value(self):
        """Test float above maximum value"""
        with pytest.raises(ValueError, match="must be at most"):
            sanitize_float(30.0, max_value=20.0)
    
    def test_invalid_float(self):
        """Test invalid float input"""
        with pytest.raises(ValueError, match="Invalid float value"):
            sanitize_float("not-a-number")
    
    def test_nan_value(self):
        """Test NaN value"""
        import math
        with pytest.raises(ValueError, match="must be a finite number"):
            sanitize_float(float('nan'))
    
    def test_infinity_value(self):
        """Test infinity value"""
        import math
        with pytest.raises(ValueError, match="must be a finite number"):
            sanitize_float(float('inf'))


class TestSanitizePathTraversal:
    """Test sanitize_path_traversal function"""
    
    def test_valid_path(self):
        """Test valid path"""
        result = sanitize_path_traversal("path/to/file")
        assert result == "path/to/file"
    
    def test_path_with_dot_dot(self):
        """Test path traversal prevention"""
        result = sanitize_path_traversal("../../../etc/passwd")
        assert ".." not in result
        assert result == "etc/passwd"
    
    def test_path_with_double_slash(self):
        """Test double slash removal"""
        result = sanitize_path_traversal("path//to//file")
        assert "//" not in result
    
    def test_path_with_leading_slash(self):
        """Test leading slash removal"""
        result = sanitize_path_traversal("/path/to/file")
        assert not result.startswith("/")
    
    def test_invalid_path_characters(self):
        """Test invalid path characters"""
        with pytest.raises(ValueError, match="Invalid path format"):
            sanitize_path_traversal("path/to/file<script>")
    
    def test_non_string_path(self):
        """Test non-string path input"""
        with pytest.raises(ValueError, match="Path must be a string"):
            sanitize_path_traversal(123)
    
    def test_complex_path_traversal(self):
        """Test complex path traversal attempt"""
        result = sanitize_path_traversal("....//....//etc/passwd")
        assert ".." not in result
        assert "//" not in result

