from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@patch('src.main.migration_service')
def test_read_root(mock_service):
    mock_service.get_zha_devices = AsyncMock(return_value=[])

    response = client.get("/")
    assert response.status_code == 200


@patch('src.main.migration_service')
def test_migrate_endpoint(mock_service):
    mock_service.migrate_to_z2m = AsyncMock(return_value=[])

    payload = {"ieees": ["ieee1"], "direction": "zha_to_z2m"}
    response = client.post("/migrate", json=payload)

    assert response.status_code == 200
    assert response.json() == {"status": "success", "results": []}
