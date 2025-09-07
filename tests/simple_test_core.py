"""
Simple Core Tests
Basic tests for core functionality
"""

import pytest
from app.core.auth import get_password_hash, verify_password, create_access_token


class TestSimpleCore:
    """Simple core functionality tests"""

    def test_password_hashing(self):
        """Test password hashing works"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        # Password should be hashed (different from original)
        assert hashed != password
        assert len(hashed) > 10  # Should be a proper hash

        # Should verify correctly
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_token_creation(self):
        """Test JWT token creation"""
        user_data = {"sub": "testuser"}
        token = create_access_token(data=user_data)

        # Should return a token
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 10  # Should be a proper JWT token

    def test_password_security(self):
        """Test that same password gives different hashes"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2

        # But both should verify the same password
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
