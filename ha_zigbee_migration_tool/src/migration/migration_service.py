from typing import List, Dict, Any, Set

from ..config.config import Settings
from ..config.logging_config import get_logger
from ..files.backup_service import BackupService
from ..files.json_adapter import JsonAdapter
from .transformer import Transformer
from ..sql.sqlite_adapter import SqliteAdapter

logger = get_logger(__name__)


class MigrationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.sql_adapter = SqliteAdapter(settings)
        self.json_adapter = JsonAdapter(settings)
        self.backup_service = BackupService(settings)
        self.transformer = Transformer(settings)

    async def get_zha_devices(self, db_path: str, registry_path: str, z2m_db_path: str) -> List[Dict[str, Any]]:
        logger.info("Fetching ZHA devices from database.")
        zha_devices_raw = self.sql_adapter.get_devices(db_path)
        zha_endpoints = self.sql_adapter.get_endpoints(db_path)
        zha_node_descriptors = self.sql_adapter.get_node_descriptors(db_path)
        logger.info(f"Found {len(zha_devices_raw)} raw devices in ZHA DB.")

        registry_device_map = await self._get_registry_device_map(registry_path)
        node_descriptor_map = {desc['ieee']: desc for desc in zha_node_descriptors}

        logger.info("Fetching existing Zigbee2MQTT devices.")
        z2m_existing_data = await self.json_adapter.read_json_lines(z2m_db_path)
        existing_z2m_ieees = self._get_existing_z2m_ieees(z2m_existing_data)
        logger.info(f"Found {len(existing_z2m_ieees)} existing devices in Z2M DB.")

        enriched_devices = self._enrich_devices(zha_devices_raw, zha_endpoints, registry_device_map,
                                                node_descriptor_map)

        migratable_devices = [
            dev for dev in enriched_devices
            if f"{self.settings.Z2M_IEEE_PREFIX}{dev['ieee'].replace(':', '').lower()}" not in existing_z2m_ieees
        ]
        logger.info(f"Found {len(migratable_devices)} devices available for migration.")
        
        return migratable_devices

    async def _get_registry_device_map(self, registry_path: str) -> Dict[str, Any]:
        logger.info("Reading device registry.")
        registry_data = await self.json_adapter.read_json(registry_path)
        registry_devices = registry_data.get('data', {}).get('devices', [])
        
        device_map = {}
        for dev in registry_devices:
            for identifier in dev.get('identifiers', []):
                if identifier[0] == self.settings.REGISTRY_IDENTIFIER_ZHA:
                    ieee = identifier[1].lower()
                    device_map[ieee] = dev
        logger.info(f"Mapped {len(device_map)} devices from registry.")
        return device_map

    def _enrich_devices(self, devices: List[Dict[str, Any]], endpoints: List[Dict[str, Any]],
                        registry_device_map: Dict[str, Any], node_descriptor_map: Dict[str, Any]) -> List[
        Dict[str, Any]]:
        enriched = []
        for dev in devices:
            if self._is_coordinator(dev):
                logger.debug(f"Skipping coordinator device: {dev.get('ieee')}")
                continue
            
            enriched.append(self._create_enriched_device(dev, endpoints, registry_device_map, node_descriptor_map))
        return enriched

    def _is_coordinator(self, dev: Dict[str, Any]) -> bool:
        return dev.get('nwk') == 0

    def _create_enriched_device(self, dev: Dict[str, Any], endpoints: List[Dict[str, Any]],
                                registry_device_map: Dict[str, Any], node_descriptor_map: Dict[str, Any]) -> Dict[
        str, Any]:
        ieee = dev.get('ieee')
        logger.debug(f"Enriching device {ieee}")
        registry_device = registry_device_map.get(ieee.lower())
        node_descriptor = node_descriptor_map.get(ieee)

        friendly_name, manufacturer, model = None, None, None
        if registry_device:
            friendly_name = registry_device.get('name_by_user') or registry_device.get('name')
            manufacturer = registry_device.get('manufacturer')
            model = registry_device.get('model')
            logger.debug(f"[{ieee}] Found in registry: name='{friendly_name}'")

        logical_type = node_descriptor.get('logical_type') if node_descriptor else None
        logger.debug(f"[{ieee}] Determined logical type: {logical_type}")

        device_endpoints = [ep for ep in endpoints if ep.get('ieee') == ieee]
        logger.debug(f"[{ieee}] Found {len(device_endpoints)} endpoints.")

        return {
            "ieee": ieee, "nwk": dev.get('nwk'), "manufacturer": manufacturer,
            "model": model, "device_type": logical_type, "friendly_name": friendly_name,
            "endpoints": device_endpoints
        }

    async def migrate_to_z2m(self, zha_db_path: str, zha_registry_path: str, z2m_db_path: str,
                             selected_ieees: List[str], backup_dir: str) -> List[Dict[str, Any]]:
        logger.info(f"Starting migration of {len(selected_ieees)} devices.")
        self.backup_service.create_backup(z2m_db_path, backup_dir)

        z2m_existing = await self.json_adapter.read_json_lines(z2m_db_path)
        existing_ieees = self._get_existing_z2m_ieees(z2m_existing)
        
        all_zha_devices = await self._get_all_zha_devices_for_migration(zha_db_path, zha_registry_path)

        results, new_z2m_entries = [], list(z2m_existing)
        for zha_dev in all_zha_devices:
            if zha_dev['ieee'] in selected_ieees:
                self._migrate_single_device(zha_dev, existing_ieees, new_z2m_entries, results)

        logger.info(f"Writing {len(new_z2m_entries)} total devices to Z2M database.")
        await self.json_adapter.write_json_lines(z2m_db_path, new_z2m_entries)
        return results

    async def _get_all_zha_devices_for_migration(self, db_path: str, registry_path: str) -> List[Dict[str, Any]]:
        """Helper to get all devices without filtering for the migration backend."""
        zha_devices = self.sql_adapter.get_devices(db_path)
        zha_endpoints = self.sql_adapter.get_endpoints(db_path)
        zha_node_descriptors = self.sql_adapter.get_node_descriptors(db_path)
        registry_device_map = await self._get_registry_device_map(registry_path)
        node_descriptor_map = {desc['ieee']: desc for desc in zha_node_descriptors}
        return self._enrich_devices(zha_devices, zha_endpoints, registry_device_map, node_descriptor_map)

    def _get_existing_z2m_ieees(self, z2m_data: List[Dict[str, Any]]) -> Set[str]:
        return {dev['ieeeAddr'].lower() for dev in z2m_data if 'ieeeAddr' in dev}

    def _migrate_single_device(self, zha_dev: Dict[str, Any], existing_ieees: Set[str],
                               new_entries: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> None:
        ieee = zha_dev['ieee']
        formatted_ieee = f"{self.settings.Z2M_IEEE_PREFIX}{ieee.replace(':', '').lower()}"

        if formatted_ieee.lower() in existing_ieees:
            logger.warning(f"[{ieee}] Device already exists in Z2M database. Skipping.")
            return

        logger.info(f"[{ieee}] Transforming device for Z2M.")
        transformed = self.transformer.transform_zha_to_z2m(zha_dev)
        new_entries.append(transformed)
        
        results.append({"ieee": ieee, "old_name": zha_dev['friendly_name'], "status": "success"})
        logger.info(f"[{ieee}] Successfully transformed and added to migration list.")
