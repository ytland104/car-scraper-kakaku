#!/bin/bash

# Install fixed cron configuration for car scraper

echo "Installing fixed car scraper cron configuration..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if the fixed cron configuration exists
CRON_FILE="$SCRIPT_DIR/cron_fixed.txt"
if [ ! -f "$CRON_FILE" ]; then
    echo "Error: $CRON_FILE not found"
    exit 1
fi

# Backup current crontab
echo "Backing up current crontab..."
crontab -l > "$PROJECT_DIR/logs/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "No existing crontab to backup"

# Install the new crontab
echo "Installing new crontab configuration..."
crontab "$CRON_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Cron configuration installed successfully!"
    echo ""
    echo "Current crontab:"
    crontab -l
    echo ""
    echo "📝 Note: The car scraper will now run every Sunday at 3:00 AM"
    echo "📂 Logs will be written to: $PROJECT_DIR/logs/cron.log"
else
    echo "❌ Failed to install cron configuration"
    exit 1
fi 