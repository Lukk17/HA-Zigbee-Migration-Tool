from unittest.mock import patch, AsyncMock

import pytest

from ha_zigbee_migration_tool.src.migration.migration_service import migration_service


@pytest.mark.asyncio
async def test_get_zha_devices_filters_existing():
    """
    Verify that get_zha_devices correctly filters out devices that already exist in Z2M.
    """
    with patch('ha_zigbee_migration_tool.src.migration.migration_service.sqlite_adapter') as mock_sql, \
            patch('ha_zigbee_migration_tool.src.migration.migration_service.json_adapter') as mock_json:
        # Arrange: Mock the data sources
        # ZHA has two devices: ieee1 (new) and ieee2 (existing)
        mock_sql.get_devices.return_value = [
            {'ieee': '00:00:00:00:00:00:00:01', 'nwk': 10},
            {'ieee': '00:00:00:00:00:00:00:02', 'nwk': 20},
        ]
        mock_sql.get_endpoints.return_value = []
        mock_sql.get_node_descriptors.return_value = [
            {'ieee': '00:00:00:00:00:00:00:01', 'logical_type': 1},
            {'ieee': '00:00:00:00:00:00:00:02', 'logical_type': 2},
        ]

        # Z2M already contains ieee2
        mock_json.read_json_lines = AsyncMock(return_value=[
            {'ieeeAddr': '0x0000000000000002'}
        ])
        # Registry for friendly names
        mock_json.read_json = AsyncMock(return_value={'data': {'devices': []}})

        # Act: Call the method under test
        devices = await migration_service.get_zha_devices(
            db_path='fake_zha.db',
            registry_path='fake_reg.json',
            z2m_db_path='fake_z2m.db'
        )

        # Assert: Only the new device (ieee1) should be returned
        assert len(devices) == 1
        assert devices[0]['ieee'] == '00:00:00:00:00:00:00:01'


def test_is_coordinator():
    assert migration_service._is_coordinator({'nwk': 0}) is True
    assert migration_service._is_coordinator({'nwk': 1}) is False
