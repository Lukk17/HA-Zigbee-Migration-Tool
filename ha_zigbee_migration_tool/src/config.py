from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Configuration
    API_PORT: int = Field(default=8099, description="Port for the FastAPI server")
    API_HOST: str = Field(default="0.0.0.0", description="Host to bind the server to")
    LOG_LEVEL: str = Field(default="INFO", description="Global logging level")

    # Paths
    OPTIONS_PATH: str = Field(default="/data/options.json", description="Path to HA options.json")
    CONFIG_DIR: str = Field(default="/config", description="Base config directory")
    ZHA_DB_PATH: str = Field(default="/config/zigbee.db", description="Path to ZHA database")
    ZHA_REGISTRY_PATH: str = Field(default="/config/.storage/core.device_registry",
                                   description="Path to ZHA device registry")
    Z2M_DB_PATH: str = Field(default="/config/zigbee2mqtt/database.db", description="Path to Zigbee2MQTT database")

    # SQL Constants
    SQL_TABLE_MAX_VERSION_QUERY: str = Field(
        default="SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ESCAPE '\\'",
        description="Query to find versioned tables"
    )
    SQL_SELECT_ALL_QUERY: str = Field(default="SELECT * FROM %s", description="Template for selecting all from table")
    TABLE_PREFIX_DEVICES: str = Field(default="devices", description="Prefix for devices table")
    TABLE_PREFIX_ENDPOINTS: str = Field(default="endpoints", description="Prefix for endpoints table")
    TABLE_PREFIX_NODE_DESCRIPTORS: str = Field(default="node_descriptors",
                                               description="Prefix for node descriptors table")
    TABLE_VERSION_SUFFIX: str = Field(default="_v%", description="Suffix for versioned tables")

    # Z2M Constants
    Z2M_TYPE_COORDINATOR: str = Field(default="Coordinator", description="Z2M Coordinator type")
    Z2M_TYPE_ROUTER: str = Field(default="Router", description="Z2M Router type")
    Z2M_TYPE_END_DEVICE: str = Field(default="EndDevice", description="Z2M EndDevice type")
    Z2M_INTERVIEW_COMPLETED: bool = Field(default=True, description="Default interview completed flag")
    Z2M_INTERVIEW_STATE_SUCCESS: str = Field(default="SUCCESSFUL", description="Default interview state")
    Z2M_IEEE_PREFIX: str = Field(default="0x", description="Prefix for Z2M IEEE addresses")

    # Migration
    DIRECTION_ZHA_TO_Z2M: str = Field(default="zha_to_z2m", description="Migration direction")

    # File Settings
    UTF8_ENCODING: str = Field(default="utf-8", description="Default file encoding")
    BACKUP_TIMESTAMP_FORMAT: str = Field(default="%Y%m%d_%H%M%S", description="Format for backup timestamps")
    BACKUP_EXTENSION: str = Field(default=".bak", description="Extension for backup files")

    # Registry
    REGISTRY_IDENTIFIER_ZHA: str = Field(default="zha", description="Identifier for ZHA in registry")

    # Default Options Fallback (Local Dev)
    DEFAULT_OPTIONS: Dict[str, str] = Field(
        default={
            "zha_db": "/config/zigbee.db",
            "zha_registry": "/config/.storage/core.device_registry",
            "z2m_db": "/config/zigbee2mqtt/database.db"
        },
        description="Fallback options if options.json missing"
    )


settings = Settings()
