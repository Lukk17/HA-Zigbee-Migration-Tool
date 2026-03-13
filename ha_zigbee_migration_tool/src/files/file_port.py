from abc import ABC, abstractmethod
from typing import List, Dict, Any


class FilePort(ABC):
    @abstractmethod
    async def read_json(self, file_path: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def read_json_lines(self, file_path: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def write_json_lines(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        pass
