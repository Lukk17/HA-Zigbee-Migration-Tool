import sqlite3

from src.config import settings
from src.sql.sqlite_adapter import sqlite_adapter


def test_extract_latest_table_name():
    tables = ["devices_v13", "devices_v14", "other"]
    result = sqlite_adapter._extract_latest_table_name(tables, settings.TABLE_PREFIX_DEVICES)
    assert result == "devices_v14"


def test_extract_latest_table_name_fallback():
    tables = ["junk"]
    result = sqlite_adapter._extract_latest_table_name(tables, settings.TABLE_PREFIX_DEVICES)
    assert result == "devices"


def test_query_all_from_table(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE devices_v1 (ieee TEXT, nwk INTEGER)")
    cursor.execute("INSERT INTO devices_v1 (ieee, nwk) VALUES ('00:11:22:33', 100)")
    conn.commit()
    conn.close()

    results = sqlite_adapter._query_all_from_table(db_path, "devices")
    assert len(results) == 1
    assert results[0]['ieee'] == '00:11:22:33'
