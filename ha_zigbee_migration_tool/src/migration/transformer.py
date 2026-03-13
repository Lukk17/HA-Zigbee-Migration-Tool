import logging
from typing import List, Dict, Any, Optional

from src.config import settings

logger = logging.getLogger(__name__)


class Transformer:
    def transform_zha_to_z2m(self, zha_device: Dict[str, Any]) -> Dict[str, Any]:
        ieee_addr = self._validate_and_get_ieee(zha_device)
        formatted_ieee = self._format_ieee(ieee_addr)

        # The endpoints are already in the correct format in the enriched zha_device object.
        # We just need to create the epList and the endpoints map.
        endpoints = zha_device.get('endpoints', [])
        ep_list = sorted([ep.get('endpoint_id') for ep in endpoints])
        z2m_endpoints = {str(ep.get('endpoint_id')): self._create_endpoint_entry(ep) for ep in endpoints}

        z2m_device = self._build_z2m_device_dict(zha_device, formatted_ieee, ep_list, z2m_endpoints)

        if zha_device.get('friendly_name'):
            z2m_device["friendly_name"] = zha_device.get('friendly_name')

        return z2m_device

    def _validate_and_get_ieee(self, zha_device: Dict[str, Any]) -> str:
        ieee_addr = zha_device.get('ieee')
        if not ieee_addr:
            raise ValueError("ZHA device missing IEEE address")
        return ieee_addr

    def _format_ieee(self, ieee_addr: str) -> str:
        return f"{settings.Z2M_IEEE_PREFIX}{ieee_addr.replace(':', '').lower()}"

    def _create_endpoint_entry(self, ep: Dict[str, Any]) -> Dict[str, Any]:
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
        return {
            "id": zha_device.get('nwk'),
            "type": self._determine_device_type(zha_device.get('device_type')),
            "ieeeAddr": ieee,
            "nwkAddr": zha_device.get('nwk'),
            "manufName": zha_device.get('manufacturer'),
            "modelId": zha_device.get('model'),
            "epList": ep_list,
            "endpoints": endpoints,
            "interviewCompleted": settings.Z2M_INTERVIEW_COMPLETED,
            "interviewState": settings.Z2M_INTERVIEW_STATE_SUCCESS,
            "meta": {}
        }

    def _determine_device_type(self, device_type_id: Optional[int]) -> str:
        if device_type_id == 0:
            return settings.Z2M_TYPE_COORDINATOR
        if device_type_id == 1:
            return settings.Z2M_TYPE_ROUTER
        return settings.Z2M_TYPE_END_DEVICE


transformer = Transformer()
