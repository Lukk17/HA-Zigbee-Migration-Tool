#!/usr/bin/env bashio

bashio::log.info "Starting HA Zigbee Migration Tool..."

# Run the main script as a module from within the src package
python3 -m src.main
