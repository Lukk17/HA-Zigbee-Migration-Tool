import json

import aiofiles
import pytest
from src.files.json_adapter import json_adapter


@pytest.mark.asyncio
async def test_read_write_json_lines(tmp_path):
    file_path = str(tmp_path / "test.jsonl")
    data = [{"a": 1}, {"b": 2}]

    await json_adapter.write_json_lines(file_path, data)

    read_data = await json_adapter.read_json_lines(file_path)
    assert read_data == data


@pytest.mark.asyncio
async def test_read_json(tmp_path):
    file_path = str(tmp_path / "test.json")
    data = {"key": "value"}

    async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
        await f.write(json.dumps(data))

    read_data = await json_adapter.read_json(file_path)
    assert read_data == data
