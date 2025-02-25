#!/bin/sh

# copy static assets to volume

# Copy static assets to the volume if they don't exist
if [ ! -d "/app/services/assets/output/static" ]; then
    cp -r /app/services/assets/static /app/services/assets/output/
fi

# Initial sync task
uv sync

# Run the other scripts once
uv run --no-sync src/gen_images.py
uv run --no-sync src/gen_item_metadata.py
uv run --no-sync src/gen_container_metadata.py
uv run --no-sync src/refresh_prices.py

# Loop to check every 60 seconds
while true; do
    current_minute=$(date +%-M)

    if [ $((current_minute % 15)) -eq 0 ]; then
        uv run --no-sync src/refresh_prices.py
    fi

    sleep 60
done
