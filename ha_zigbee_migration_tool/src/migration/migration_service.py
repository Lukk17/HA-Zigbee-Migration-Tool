import logging
from typing import List, Dict, Any, Set

from src.config import settings
from src.files.backup_service import backup_service
from src.files.json_adapter import json_adapter
from src.migration.transformer import transformer
from src.sql.sqlite_adapter import sqlite_adapter

logger = logging.getLogger(__name__)


class MigrationService:
    async def get_zha_devices(self, db_path: str, registry_path: str, z2m_db_path: str) -> List[Dict[str, Any]]:
        zha_devices_raw = sqlite_adapter.get_devices(db_path)
        zha_endpoints = sqlite_adapter.get_endpoints(db_path)
        zha_node_descriptors = sqlite_adapter.get_node_descriptors(db_path)

        registry_device_map = await self._get_registry_device_map(registry_path)
        node_descriptor_map = {desc['ieee']: desc for desc in zha_node_descriptors}

        # Get existing Z2M IEEE addresses to filter them out
        z2m_existing_data = await json_adapter.read_json_lines(z2m_db_path)
        existing_z2m_ieees = self._get_existing_z2m_ieees(z2m_existing_data)

        enriched_devices = self._enrich_devices(zha_devices_raw, zha_endpoints, registry_device_map,
                                                node_descriptor_map)

        # Filter out devices that already exist in Z2M
        migratable_devices = [
            dev for dev in enriched_devices
            if f"{settings.Z2M_IEEE_PREFIX}{dev['ieee'].replace(':', '').lower()}" not in existing_z2m_ieees
        ]

        return migratable_devices

    async def _get_registry_device_map(self, registry_path: str) -> Dict[str, Any]:
        registry_data = await json_adapter.read_json(registry_path)
        registry_devices = registry_data.get('data', {}).get('devices', [])

        device_map = {}
        for dev in registry_devices:
            for identifier in dev.get('identifiers', []):
                if identifier[0] == settings.REGISTRY_IDENTIFIER_ZHA:
                    ieee = identifier[1].lower()
                    device_map[ieee] = dev
        return device_map

    def _enrich_devices(self, devices: List[Dict[str, Any]], endpoints: List[Dict[str, Any]],
                        registry_device_map: Dict[str, Any], node_descriptor_map: Dict[str, Any]) -> List[
        Dict[str, Any]]:
        enriched = []
        for dev in devices:
            if self._is_coordinator(dev):
                continue

            enriched.append(self._create_enriched_device(dev, endpoints, registry_device_map, node_descriptor_map))
        return enriched

    def _is_coordinator(self, dev: Dict[str, Any]) -> bool:
        return dev.get('nwk') == 0

    def _create_enriched_device(self, dev: Dict[str, Any], endpoints: List[Dict[str, Any]],
                                registry_device_map: Dict[str, Any], node_descriptor_map: Dict[str, Any]) -> Dict[
        str, Any]:
        ieee = dev.get('ieee')
        registry_device = registry_device_map.get(ieee.lower())
        node_descriptor = node_descriptor_map.get(ieee)

        friendly_name = None
        manufacturer = None
        model = None
        if registry_device:
            friendly_name = registry_device.get('name_by_user') or registry_device.get('name')
            manufacturer = registry_device.get('manufacturer')
            model = registry_device.get('model')

        logical_type = node_descriptor.get('logical_type') if node_descriptor else None

        return {
            "ieee": ieee,
            "nwk": dev.get('nwk'),
            "manufacturer": manufacturer,
            "model": model,
            "device_type": logical_type,
            "friendly_name": friendly_name,
            "endpoints": [ep for ep in endpoints if ep.get('ieee') == ieee]
        }

    async def migrate_to_z2m(self, zha_db_path: str, zha_registry_path: str, z2m_db_path: str,
                             selected_ieees: List[str], backup_dir: str) -> List[Dict[str, Any]]:
        backup_service.create_backup(z2m_db_path, backup_dir)

        zha_data = await self.get_zha_devices(zha_db_path, zha_registry_path, z2m_db_path)
        z2m_existing = await json_adapter.read_json_lines(z2m_db_path)

        existing_ieees = self._get_existing_z2m_ieees(z2m_existing)

        results = []
        new_z2m_entries = list(z2m_existing)

        # We need to re-fetch and re-enrich all devices here, not just the migratable ones,
        # to ensure we can migrate a device that was previously filtered from the UI.
        all_zha_devices = await self._get_all_zha_devices_for_migration(zha_db_path, zha_registry_path)

        for zha_dev in all_zha_devices:
            if zha_dev['ieee'] in selected_ieees:
                self._migrate_single_device(zha_dev, existing_ieees, new_z2m_entries, results)

        await json_adapter.write_json_lines(z2m_db_path, new_z2m_entries)
        return results

    async def _get_all_zha_devices_for_migration(self, db_path: str, registry_path: str) -> List[Dict[str, Any]]:
        """Helper to get all devices without filtering for the migration backend."""
        zha_devices = sqlite_adapter.get_devices(db_path)
        zha_endpoints = sqlite_adapter.get_endpoints(db_path)
        zha_node_descriptors = sqlite_adapter.get_node_descriptors(db_path)
        registry_device_map = await self._get_registry_device_map(registry_path)
        node_descriptor_map = {desc['ieee']: desc for desc in zha_node_descriptors}
        return self._enrich_devices(zha_devices, zha_endpoints, registry_device_map, node_descriptor_map)

    def _get_existing_z2m_ieees(self, z2m_data: List[Dict[str, Any]]) -> Set[str]:
        return {dev['ieeeAddr'].lower() for dev in z2m_data if 'ieeeAddr' in dev}

    def _migrate_single_device(self, zha_dev: Dict[str, Any], existing_ieees: Set[str],
                               new_entries: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
        formatted_ieee = f"{settings.Z2M_IEEE_PREFIX}{zha_dev['ieee'].replace(':', '').lower()}"

        if formatted_ieee.lower() in existing_ieees:
            logger.info(f"[Migration] Device {formatted_ieee} already in Z2M, skipping")
            return

        transformed = transformer.transform_zha_to_z2m(zha_dev)

        new_entries.append(transformed)
        results.append({
            "ieee": zha_dev['ieee'],
            "old_name": zha_dev['friendly_name'],
            "status": "success"
        })


migration_service = MigrationService()
