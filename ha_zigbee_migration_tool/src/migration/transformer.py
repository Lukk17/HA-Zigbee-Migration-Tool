from typing import List, Dict, Any, Optional

from ..config.config import Settings
from ..config.logging_config import get_logger

logger = get_logger(__name__)


class Transformer:
    def __init__(self, settings: Settings):
        self.settings = settings

    def transform_zha_to_z2m(self, zha_device: Dict[str, Any]) -> Dict[str, Any]:
        ieee_addr = self._validate_and_get_ieee(zha_device)
        logger.debug(f"[{ieee_addr}] Starting transformation.")
        
        formatted_ieee = self._format_ieee(ieee_addr)
        
        endpoints = zha_device.get('endpoints', [])
        ep_list = sorted([ep.get('endpoint_id') for ep in endpoints])
        z2m_endpoints = {str(ep.get('endpoint_id')): self._create_endpoint_entry(ep) for ep in endpoints}
        logger.debug(f"[{ieee_addr}] Transformed {len(ep_list)} endpoints.")

        z2m_device = self._build_z2m_device_dict(zha_device, formatted_ieee, ep_list, z2m_endpoints)
        
        if zha_device.get('friendly_name'):
            z2m_device["friendly_name"] = zha_device.get('friendly_name')
            logger.debug(f"[{ieee_addr}] Applied friendly name: {zha_device.get('friendly_name')}")

        logger.info(f"[{ieee_addr}] Transformation complete.")
        return z2m_device

    def _validate_and_get_ieee(self, zha_device: Dict[str, Any]) -> str:
        ieee_addr = zha_device.get('ieee')
        if not ieee_addr:
            logger.error("Attempted to transform a device with no IEEE address.")
            raise ValueError("ZHA device missing IEEE address")
        return ieee_addr

    def _format_ieee(self, ieee_addr: str) -> str:
        return f"{self.settings.Z2M_IEEE_PREFIX}{ieee_addr.replace(':', '').lower()}"

    def _create_endpoint_entry(self, ep: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug(f"Creating endpoint entry for endpoint ID: {ep.get('endpoint_id')}")
        return {
            "profId": ep.get('profile_id'),
            "epId": ep.get('endpoint_id'),
            "devId": ep.get('device_type'),
            "inClusterList": [],
            "outClusterList": [],
            "clusters": {},
            "binds": [],
            "configuredReportings": [],
            "meta": {}
        }

    def _build_z2m_device_dict(self, zha_device: Dict[str, Any], ieee: str, ep_list: List[int],
                               endpoints: Dict[str, Any]) -> Dict[str, Any]:
        device_type = self._determine_device_type(zha_device.get('device_type'))
        logger.debug(f"[{zha_device.get('ieee')}] Building Z2M device dictionary with type: {device_type}")
        return {
            "id": zha_device.get('nwk'),
            "type": device_type,
            "ieeeAddr": ieee,
            "nwkAddr": zha_device.get('nwk'),
            "manufName": zha_device.get('manufacturer'),
            "modelId": zha_device.get('model'),
            "epList": ep_list,
            "endpoints": endpoints,
            "interviewCompleted": self.settings.Z2M_INTERVIEW_COMPLETED,
            "interviewState": self.settings.Z2M_INTERVIEW_STATE_SUCCESS,
            "meta": {}
        }

    def _determine_device_type(self, device_type_id: Optional[int]) -> str:
        if device_type_id == 0:
            return self.settings.Z2M_TYPE_COORDINATOR
        if device_type_id == 1:
            return self.settings.Z2M_TYPE_ROUTER
        return self.settings.Z2M_TYPE_END_DEVICE
