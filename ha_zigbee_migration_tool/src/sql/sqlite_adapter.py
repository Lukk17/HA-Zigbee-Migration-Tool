import logging
import sqlite3
from typing import List, Dict, Any
from ..config.config import Settings
from .sql_port import SqlPort

logger = logging.getLogger(__name__)

class SqliteAdapter(SqlPort):
    def __init__(self, settings: Settings):
        self.settings = settings

    def _find_highest_version_table(self, cursor: sqlite3.Cursor, base_name: str) -> str:
        cursor.execute(self.settings.SQL_TABLE_MAX_VERSION_QUERY, (f"{base_name}{self.settings.TABLE_VERSION_SUFFIX}",))
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            return base_name

        return self._extract_latest_table_name(tables, base_name)

    def _extract_latest_table_name(self, tables: List[str], base_name: str) -> str:
        versions = []
        for table in tables:
            try:
                version_str = table.split('_v')[-1]
                versions.append((int(version_str), table))
            except (ValueError, IndexError):
                continue

        if not versions:
            return base_name

        return max(versions, key=lambda x: x[0])[1]

    def _query_all_from_table(self, db_path: str, base_table_name: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        table_name = self._find_highest_version_table(cursor, base_table_name)
        cursor.execute(self.settings.SQL_SELECT_ALL_QUERY % table_name)
        results = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return results

    def get_devices(self, db_path: str) -> List[Dict[str, Any]]:
        return self._query_all_from_table(db_path, self.settings.TABLE_PREFIX_DEVICES)

    def get_endpoints(self, db_path: str) -> List[Dict[str, Any]]:
        return self._query_all_from_table(db_path, self.settings.TABLE_PREFIX_ENDPOINTS)

    def get_node_descriptors(self, db_path: str) -> List[Dict[str, Any]]:
        return self._query_all_from_table(db_path, self.settings.TABLE_PREFIX_NODE_DESCRIPTORS)
