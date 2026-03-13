-- =================================================================================
-- GENERIC ANONYMIZATION TEMPLATE FOR ZHA DATABASE (zigbee.db)
--
-- PURPOSE:
-- To safely and completely anonymize a ZHA database file, making it suitable for
-- public sharing as an example.
--
-- HOW TO USE THIS TEMPLATE:
--
-- 1. **BACKUP YOUR DATABASE:** Before running any part of this script, make a
--    copy of your real 'zigbee.db' file.
--
-- 2. **FIND THE LATEST TABLE VERSION:**
--    Run the following query on your database to find the latest version number
--    (e.g., 14, 15, etc.).
--
--    SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'devices_v%';
--
--    Look for the highest number after '_v'. This is your version number.
--
-- 3. **FIND AND REPLACE THE VERSION PLACEHOLDER:**
--    In this file, find all occurrences of '_vX' and replace them with the
--    latest version string (e.g., replace all '_vX' with '_v14').
--
-- 4. **CUSTOMIZE THE IEEE ADDRESS MAPPINGS:**
--    The section marked "CUSTOMIZE THIS SECTION" contains templates for replacing
--    real IEEE addresses with fake ones. You MUST update this section with the
--    real IEEE addresses from your database and decide on corresponding fake ones.
--
-- 5. **EXECUTE THE SCRIPT:**
--    Run the entire modified script on your copied database file.
--
-- =================================================================================

BEGIN TRANSACTION;

-- ---------------------------------------------------------------------------------
-- Step 1: Drop all obsolete and sensitive tables.
-- This cleans up old versions and drops the network backups table entirely,
-- which is the safest way to remove the network key.
-- ---------------------------------------------------------------------------------
DROP TABLE IF EXISTS attributes_cache_v13;
DROP TABLE IF EXISTS clusters_v13;
DROP TABLE IF EXISTS devices_v13;
DROP TABLE IF EXISTS endpoints_v13;
DROP TABLE IF EXISTS group_members_v13;
DROP TABLE IF EXISTS groups_v13;
DROP TABLE IF EXISTS neighbors_v13;
DROP TABLE IF EXISTS network_backups_v13;
DROP TABLE IF EXISTS node_descriptors_v13;
DROP TABLE IF EXISTS relays_v13;
DROP TABLE IF EXISTS routes_v13;
DROP TABLE IF EXISTS unsupported_attributes_v13;
DROP TABLE IF EXISTS network_backups_vX; -- Replaced with latest version

-- ---------------------------------------------------------------------------------
-- Step 2: Anonymize all network-specific identifiers.
-- ---------------------------------------------------------------------------------

-- Anonymize the Extended PAN ID in the neighbors table. This is a network-wide ID.
UPDATE neighbors_vX
SET extended_pan_id = '00:00:00:00:00:00:00:00'
WHERE ROWID IN (SELECT ROWID FROM neighbors_vX);

-- ---------------------------------------------------------------------------------
-- Step 3: Anonymize all device-specific IEEE addresses.
--
-- === START: IEEE ADDRESS MAPPING (CUSTOMIZE THIS SECTION) ===
--
-- For each of your real devices, you need to create a block of UPDATE statements.
-- Use the template below and replace '[REAL_IEEE_ADDRESS]' and '[FAKE_IEEE_ADDRESS]'.
--
-- --- Template for one device ---
-- UPDATE devices_vX          SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE endpoints_vX        SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE clusters_vX         SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE node_descriptors_vX SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE neighbors_vX        SET device_ieee = '[FAKE_IEEE_ADDRESS]' WHERE device_ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE neighbors_vX        SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE relays_vX           SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE routes_vX           SET device_ieee = '[FAKE_IEEE_ADDRESS]' WHERE device_ieee = '[REAL_IEEE_ADDRESS]';
-- UPDATE attributes_cache_vX SET ieee = '[FAKE_IEEE_ADDRESS]' WHERE ieee = '[REAL_IEEE_ADDRESS]';
--
-- --- Example block for a device ---
-- UPDATE devices_vX          SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE endpoints_vX        SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE clusters_vX         SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE node_descriptors_vX SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE neighbors_vX        SET device_ieee = '00:00:00:00:00:00:00:01' WHERE device_ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE neighbors_vX        SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE relays_vX           SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE routes_vX           SET device_ieee = '00:00:00:00:00:00:00:01' WHERE device_ieee = '04:87:27:ff:fe:22:28:bd';
-- UPDATE attributes_cache_vX SET ieee = '00:00:00:00:00:00:00:01' WHERE ieee = '04:87:27:ff:fe:22:28:bd';
--
-- === END: IEEE ADDRESS MAPPING (CUSTOMIZE THIS SECTION) ===
-- ---------------------------------------------------------------------------------


-- ---------------------------------------------------------------------------------
-- Step 4: Clear potentially sensitive data from cache and group tables.
-- ---------------------------------------------------------------------------------

-- Nullify the 'value' column in the attributes cache to remove all device state history.
UPDATE attributes_cache_vX
SET value = NULL
WHERE ROWID IN (SELECT ROWID FROM attributes_cache_vX);

-- Anonymize user-defined group names to prevent leaking room or area information.
UPDATE groups_vX
SET name = 'Anonymized Group ' || group_id
WHERE ROWID IN (SELECT ROWID FROM groups_vX);

-- ---------------------------------------------------------------------------------
-- Step 5: Finalize the transaction.
-- ---------------------------------------------------------------------------------
COMMIT;