#!/bin/bash
# Watchdog: checks if XML downloads are progressing
# Alerts if no new files appear in 2 minutes

CACHE_DIR="/Users/anushasubramanian/Desktop/Projects/freelance/data/.xml_cache"
CHECK_INTERVAL=60  # seconds between checks
STALL_THRESHOLD=2  # alert after this many checks with no progress

last_count=0
stall_count=0

while true; do
    current_count=$(find "$CACHE_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    timestamp=$(date '+%H:%M:%S')

    if [ "$current_count" -eq "$last_count" ] && [ "$current_count" -gt 0 ]; then
        stall_count=$((stall_count + 1))
        if [ "$stall_count" -ge "$STALL_THRESHOLD" ]; then
            echo "⚠️  [$timestamp] STALLED — stuck at $current_count files for $((stall_count * CHECK_INTERVAL))s"
        fi
    else
        stall_count=0
        rate=$((current_count - last_count))
        remaining=$((6071 - current_count))
        if [ "$rate" -gt 0 ]; then
            eta_min=$((remaining / rate))
            echo "✓  [$timestamp] $current_count / 6071 files (+$rate) — ~${eta_min}min remaining"
        else
            echo "✓  [$timestamp] $current_count / 6071 files"
        fi
    fi

    last_count=$current_count

    # Stop if we're done
    if [ "$current_count" -ge 6071 ]; then
        echo "✓  [$timestamp] COMPLETE — $current_count files downloaded"
        exit 0
    fi

    sleep $CHECK_INTERVAL
done
