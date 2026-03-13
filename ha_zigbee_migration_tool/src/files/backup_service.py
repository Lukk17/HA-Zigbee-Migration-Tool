import logging
import os
import shutil
from datetime import datetime
from ..config.config import Settings

logger = logging.getLogger(__name__)

class BackupService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create_backup(self, source_path: str, backup_dir: str) -> str:
        self._validate_source_exists(source_path)
        self._ensure_backup_dir_exists(backup_dir)

        filename = os.path.basename(source_path)
        timestamp = datetime.now().strftime(self.settings.BACKUP_TIMESTAMP_FORMAT)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}{self.settings.BACKUP_EXTENSION}")

        shutil.copy2(source_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path

    def _validate_source_exists(self, source_path: str) -> None:
        if not os.path.exists(source_path):
            logger.error(f"Backup source file not found: {source_path}")
            raise FileNotFoundError(f"Source file not found: {source_path}")

    def _ensure_backup_dir_exists(self, backup_dir: str) -> None:
        if not os.path.exists(backup_dir):
            logger.info(f"Creating backup directory: {backup_dir}")
            os.makedirs(backup_dir)
