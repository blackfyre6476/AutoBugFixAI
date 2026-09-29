import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path for test runner resolution
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Fixture providing a FastAPI TestClient instance."""
    with TestClient(app) as client:
        yield client
