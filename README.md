# HA-Zigbee-Migration-Tool

Automated local migration of Zigbee devices between ZHA and Zigbee2MQTT without requiring physical access or re-pairing.

---

## Usage Workflow

**IMPORTANT:** To prevent database corruption, you must stop the Zigbee2MQTT add-on before running the migration.

1.  Go to **Settings > Add-ons** and select the **Zigbee2MQTT** add-on.
2.  Click **Stop**.
3.  Go to the **HA Zigbee Migration Tool** add-on and click **Start**.
4.  Perform the migration using the web UI.
5.  When you are finished, **Stop** the HA Zigbee Migration Tool add-on.
6.  Go back to the **Zigbee2MQTT** add-on and click **Start**. It will now load with the migrated devices.

---

### Testing the Add-on

To test the add-on locally on your Home Assistant instance, you need to transfer the add-on directory to your server.

#### Files To Transfer

Copy the entire `ha_zigbee_migration_tool` directory to your Home Assistant server via SFTP. Place it inside the `/addons/` directory. 

The final path on your server must look exactly like this:
`/addons/ha_zigbee_migration_tool/config.yaml`

The table below lists the files inside the `ha_zigbee_migration_tool` directory and whether they are required for the add-on to function.

| File or Directory | Required | Explanation |
|---|---|---|
| `config.yaml` | Yes | Tells the Supervisor how to display the add-on and sets system permissions. |
| `Dockerfile` | Yes | Instructs the Supervisor how to build the container natively on HA. |
| `pyproject.toml` | Yes | Read by the Docker builder to install Python dependencies. |
| `src/` | Yes | Contains your actual Python application code. |
| `.dockerignore` | Yes | **Critical.** Tells the Docker builder to ignore unnecessary files, keeping the final image small and secure. |
| `tests/` | No | Not required for the add-on to run. It is safe to copy, as it will be ignored by the Docker build process. |
| `.env` | No | **Do not copy.** This file is for local development only and has no effect in the add-on environment. |

---

#### Installation Steps

1. Stop Zigbee2MQTT: Before copying the files, ensure the Zigbee2MQTT app is stopped to prevent file access conflicts.
2. Connect to Home Assistant via SFTP (e.g., using FileZilla).
3. Upload the `ha_zigbee_migration_tool` folder directly into the `/addons/` directory. 
4. Open your Home Assistant web interface. 
5. Go to `Settings` > `Apps`, then click the `Install app` button in the bottom right corner. 
6. Click the refresh icon shaped like a circular arrow in the top right corner. 
7. Refresh your web browser. 
8. Find your migration tool in the `Local apps` section. 
9. Click on it and select `Install`. 
10. After the build finishes, verify the settings on the Configuration tab, then click Start on the Info tab.
---

## Local Development

This project is set up for easy local development and testing using a set of anonymized example files.

### 1. Local Environment Setup

Ensure you have Python 3.12+ installed. It is recommended to use a virtual environment.

```bash
# Activate the provided virtual environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install runtime and test dependencies
pip install "./ha_zigbee_migration_tool[test]"
```

### 2. Configure for Local Testing

For local development, the application uses a `.env` file to override the default production paths and point to the test data in the `examples` folder.

Create a file named `.env` inside the `ha_zigbee_migration_tool` directory with the following content:

```
# Local development environment settings for overriding config.py
# This file is for local testing only and should NOT be committed to git.

# Set the paths to your example files.
# These paths are relative to the `ha_zigbee_migration_tool` directory where main.py is run.
ZHA_DB_PATH="../examples/ZHA/zigbee.db"
ZHA_REGISTRY_PATH="../examples/ZHA/core.device_registry"
Z2M_DB_PATH="../examples/Z2M/database.db"

# Use a dummy options.json from the root examples folder
OPTIONS_PATH="../examples/options.json"
```

### 3. Running the Application Locally

Once the `.env` file is in place, you can run the application directly:

```bash
# From the root of the project
python ha_zigbee_migration_tool/src/main.py
```

The web server will start, and the UI will be populated with the data from the `examples` folder.

### 4. Running Tests

All tests are located in the `ha_zigbee_migration_tool/tests` directory.

```bash
python -m pytest ha_zigbee_migration_tool/tests --verbose
```

---

## Example Data

The `examples` directory provides a complete set of fully anonymized data for testing the migration tool.

*   `ZHA/`: Contains `zigbee.db` and `core.device_registry` from a ZHA installation.
*   `Z2M/`: Contains `database.db` from a Zigbee2MQTT installation.
*   `options.json`: A dummy options file required by the add-on structure.
*   `anonymization.sql`: A generic SQL template that can be used to anonymize your own `zigbee.db` file if you wish to create a new set of test data.

### Anonymization Details

The example files have been carefully anonymized to remove all sensitive information. The following table details what was changed in the `zigbee.db` file.

**This is a critical security step. Do not share your own database files without performing these steps.**

| Table Name                 | Contains Confidential Data? | What is the Confidential Data?                                                                                             | Anonymization Action                               |
| -------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `network_backups_v14`      | **Yes (Critical Risk)**     | `backup_json`: Contains the Zigbee Network Key inside a JSON blob.                                                         | **Table dropped entirely.**                        |
| `attributes_cache_v14`     | **Yes (High Risk)**         | `value`: Contains last known states of devices (e.g., lock status, temperature). `ieee`: Links to a real device.            | `value` column set to `NULL`. `ieee` anonymized.   |
| `neighbors_v14`            | **Yes (Topology)**          | `device_ieee`, `ieee`, `extended_pan_id`: Defines the physical mesh network layout using real IEEE addresses.                | All three columns (`device_ieee`, `ieee`, `extended_pan_id`) anonymized. |
| `devices_v14`              | **Yes (High Risk)**         | `ieee`: The unique IEEE address of your real devices.                                                                      | `ieee` addresses replaced with fake ones.          |
| `routes_v14`               | **Yes (Topology)**          | `device_ieee`: Defines network routing paths using real IEEE addresses.                                                    | `device_ieee` anonymized.                          |
| `groups_v14`               | **Yes (Personal)**          | `name`: User-defined names for groups (e.g., "Living Room Lights").                                                        | `name` replaced with generic "Anonymized Group X". |
| `endpoints_v14`            | **Yes (Linkable)**          | `ieee`: Links endpoints to a specific device's real IEEE address.                                                          | `ieee` anonymized.                                 |
| `clusters_v14`             | **Yes (Linkable)**          | `ieee`: Links clusters to a specific device's real IEEE address.                                                           | `ieee` anonymized.                                 |
| `node_descriptors_v14`     | **Yes (Linkable)**          | `ieee`: Links descriptors to a specific device's real IEEE address.                                                        | `ieee` anonymized.                                 |
| `relays_v14`               | **Yes (Topology)**          | `ieee`: Lists which devices are acting as relays using their real IEEE addresses.                                          | `ieee` anonymized.                                 |
