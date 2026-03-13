import json
import logging
from typing import List, Dict, Any
import aiofiles
from ..config.config import Settings
from .file_port import FilePort

logger = logging.getLogger(__name__)

class JsonAdapter(FilePort):
    def __init__(self, settings: Settings):
        self.settings = settings

    async def read_json(self, file_path: str) -> Dict[str, Any]:
        async with aiofiles.open(file_path, mode='r', encoding=self.settings.UTF8_ENCODING) as file:
            content = await file.read()
            return json.loads(content)

    async def read_json_lines(self, file_path: str) -> List[Dict[str, Any]]:
        data = []
        async with aiofiles.open(file_path, mode='r', encoding=self.settings.UTF8_ENCODING) as file:
            async for line in file:
                if line.strip():
                    data.append(json.loads(line))
        return data

    async def write_json_lines(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        async with aiofiles.open(file_path, mode='w', encoding=self.settings.UTF8_ENCODING) as file:
            for entry in data:
                await file.write(json.dumps(entry) + '\n')
