import os

import pytest
from src.config import settings
from src.files.backup_service import backup_service


def test_create_backup(tmp_path):
    source = tmp_path / "source.db"
    source.write_text("content")
    backup_dir = tmp_path / "backups"

    backup_path = backup_service.create_backup(str(source), str(backup_dir))

    assert os.path.exists(backup_path)
    assert backup_path.endswith(settings.BACKUP_EXTENSION)
    assert os.path.dirname(backup_path) == str(backup_dir)


def test_create_backup_no_source():
    with pytest.raises(FileNotFoundError):
        backup_service.create_backup("nonexistent.file", "some_dir")
