"""
Pytest configuration for compliance tests
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_database_url():
    """Get test database URL"""
    return os.getenv('TEST_DATABASE_URL', 'postgresql://test:test@localhost:5433/test_db')

