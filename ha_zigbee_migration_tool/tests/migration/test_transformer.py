from ha_zigbee_migration_tool.src.config import settings
from ha_zigbee_migration_tool.src.migration.transformer import transformer


def test_transform_zha_to_z2m():
    # Arrange: Create a single, enriched ZHA device object, as the service now provides.
    zha_device = {
        'ieee': '04:87:27:ff:fe:22:28:bd',
        'nwk': 1234,
        'manufacturer': 'TestManuf',
        'model': 'TestModel',
        'device_type': 1,
        'friendly_name': "My Device",
        'endpoints': [
            {
                'device_ieee': '04:87:27:ff:fe:22:28:bd',
                'endpoint_id': 1,
                'profile_id': 260,
                'device_type': 101
            }
        ]
    }

    # Act: Call the transformer with the single device object.
    result = transformer.transform_zha_to_z2m(zha_device)

    # Assert
    assert result['ieeeAddr'] == f"{settings.Z2M_IEEE_PREFIX}048727fffe2228bd"
    assert result['nwkAddr'] == 1234
    assert result['manufName'] == 'TestManuf'
    assert result['modelId'] == 'TestModel'
    assert result['friendly_name'] == "My Device"
    assert result['type'] == "Router"
    assert result['interviewCompleted'] == settings.Z2M_INTERVIEW_COMPLETED
    assert "1" in result['endpoints']
    assert result['epList'] == [1]


def test_determine_device_type():
    assert transformer._determine_device_type(0) == "Coordinator"
    assert transformer._determine_device_type(1) == "Router"
    assert transformer._determine_device_type(2) == "EndDevice"
    assert transformer._determine_device_type(None) == "EndDevice"
