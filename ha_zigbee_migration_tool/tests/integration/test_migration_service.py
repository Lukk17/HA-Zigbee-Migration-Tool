import json
from pathlib import Path

import pytest
from deepdiff import DeepDiff

from ha_zigbee_migration_tool.src.migration.migration_service import migration_service

# Define project root relative to this test file
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


@pytest.mark.asyncio
async def test_migrate_to_z2m_full_integration():
    """
    Integration test for the full ZHA to Z2M migration process.
    It uses the anonymized example files and compares the output
    to a known-good "golden" file.
    """
    # Define paths to the test files relative to the project root
    zha_db_path = PROJECT_ROOT / "examples/ZHA/zigbee.db"
    zha_registry_path = PROJECT_ROOT / "examples/ZHA/core.device_registry"
    z2m_db_path = PROJECT_ROOT / "examples/Z2M/database.db"
    expected_output_path = PROJECT_ROOT / "examples/Z2M/expected/database.db"

    # Create a temporary directory for the output and backup
    temp_dir = Path("./build/test-output")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_output_path = temp_dir / "database.db"

    # In a real scenario, the user selects from the UI, which shows a filtered list.
    # The backend then receives a list of all devices the user wants to migrate.
    # To simulate this, we get ALL devices first, then pass the selected ones to the backend.
    all_zha_devices = await migration_service._get_all_zha_devices_for_migration(
        str(zha_db_path), str(zha_registry_path)
    )
    selected_ieees = [dev['ieee'] for dev in all_zha_devices]

    # Copy the original Z2M database to the temp location to simulate a real run
    original_z2m_content = z2m_db_path.read_text()
    temp_output_path.write_text(original_z2m_content)

    # Run the migration
    await migration_service.migrate_to_z2m(
        zha_db_path=str(zha_db_path),
        zha_registry_path=str(zha_registry_path),
        z2m_db_path=str(temp_output_path),
        selected_ieees=selected_ieees,
        backup_dir=str(temp_dir)
    )

    # Load the generated and expected files
    with open(temp_output_path, 'r') as f:
        generated_lines = [json.loads(line) for line in f]

    with open(expected_output_path, 'r') as f:
        expected_lines = [json.loads(line) for line in f]

    # Create a dictionary from the lists for easier comparison by deepdiff
    generated_map = {d['ieeeAddr']: d for d in generated_lines}
    expected_map = {d['ieeeAddr']: d for d in expected_lines}

    # Use DeepDiff to compare the two dictionaries
    diff = DeepDiff(expected_map, generated_map, ignore_order=True)

    # Assert that there are no differences. The conftest.py hook will format the output.
    assert not diff, f"Migration output does not match expected output:\n{diff.pretty()}"
