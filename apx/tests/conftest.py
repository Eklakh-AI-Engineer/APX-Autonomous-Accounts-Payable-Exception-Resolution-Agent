"""Pytest configuration for API tests."""

import os
print(f"CONFTEST: Setting APX_API_API_KEYS")
os.environ["APX_API_API_KEYS"] = "admin-key:admin:admin1,operator-key:operator:operator1,approver-key:approver:approver1:human_review|finance_approval,reader-key:reader:reader1"
print(f"CONFTEST: APX_API_API_KEYS = {os.environ.get('APX_API_API_KEYS')}")

# Reset API settings to pick up new environment variables
from apx.api.config import reset_api_settings
reset_api_settings()

import pytest
from apx.persistence.database import reset_database

@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test."""
    reset_database()
    yield
    reset_database()
