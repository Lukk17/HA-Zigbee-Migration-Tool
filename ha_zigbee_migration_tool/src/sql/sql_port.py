from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SqlPort(ABC):
    @abstractmethod
    def get_devices(self, db_path: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_endpoints(self, db_path: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_node_descriptors(self, db_path: str) -> List[Dict[str, Any]]:
        pass
