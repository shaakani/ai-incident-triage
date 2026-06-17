#!/bin/bash
# Watches the logs folder and triggers triage on new .log files

LOG_DIR="logs"
PROCESSED_DIR="logs/processed"

mkdir -p "$PROCESSED_DIR"

echo "Watching $LOG_DIR for new log files..."

while true; do
    for logfile in "$LOG_DIR"/*.log; do
        [ -f "$logfile" ] || continue
        filename=$(basename "$logfile")
        if [ ! -f "$PROCESSED_DIR/$filename.done" ]; then
            echo "New log detected: $filename"
            source venv/bin/activate
            python main.py --log "$logfile"
            touch "$PROCESSED_DIR/$filename.done"
            echo "Triage complete for: $filename"
        fi
    done
    sleep 30
done