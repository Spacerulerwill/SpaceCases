# sync
uv sync

# run once so we have an initial leaderboard
uv run --no-sync gen_leaderboards.py

# then run once every 5 minutes
while true; do
    current_minute=$(date +%-M)

    if [ $((current_minute % 5)) -eq 0 ]; then
        uv run --no-sync gen_leaderboards.py
    fi

    sleep 60
done
