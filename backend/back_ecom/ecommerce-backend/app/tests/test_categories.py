import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from ..main import app


class TestCategoryManagement:
    """Test cases for category management."""

    def test_create_category_success(self, client):
        """Test successful category creation."""
        test_data = {
            "name": "Saree",
            "slug": "saree",
            "description": "Traditional Indian sarees"
        }
        
        with patch('app.core.crud.category.get_category_crud') as mock_crud:
            mock_crud.return_value.create_category.return_value = "test_category_id"
            mock_crud.return_value.get_category_by_id.return_value = {
                "id": "test_category_id",
                "name": "Saree",
                "slug": "saree",
                "description": "Traditional Indian sarees"
            }
            
            response = client.post("/api/v1/categories/", json=test_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)
